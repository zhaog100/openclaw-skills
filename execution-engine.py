#!/usr/bin/env python3
"""
Workflow Execution Engine
Manages the running and monitoring of automation workflows with self-healing capabilities

This module provides intelligent workflow execution, error recovery, and performance monitoring.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import uuid
import time

logger = logging.getLogger(__name__)

@dataclass
class WorkflowStep:
    """Individual step in a workflow"""
    name: str
    type: str
    config: Dict[str, Any]
    timeout_seconds: int
    retry_config: Dict[str, Any]

@dataclass
class WorkflowInstance:
    """Individual workflow execution instance"""
    id: str
    workflow_id: str
    status: str  # pending, running, completed, failed, cancelled
    started_at: datetime
    completed_at: Optional[datetime]
    current_step: int
    logs: List[Dict]
    metrics: Dict
    steps: List[WorkflowStep]

class ExecutionEngine:
    """Intelligent workflow execution engine with self-healing capabilities"""

    def __init__(self):
        self.active_instances = {}
        self.completed_instances = {}
        self.error_handlers = {}
        self.monitoring_enabled = True
        self.max_concurrent_executions = 10
        self.running_executions = 0

    async def execute_workflow(self, workflow_spec: Dict) -> str:
        """Execute a workflow and return instance ID"""
        instance_id = str(uuid.uuid4())

        # Create workflow instance
        steps = [self._create_step(step_data) for step_data in workflow_spec['steps']]

        instance = WorkflowInstance(
            id=instance_id,
            workflow_id=workflow_spec['id'],
            status='pending',
            started_at=datetime.now(),
            completed_at=None,
            current_step=0,
            logs=[],
            metrics={},
            steps=steps
        )

        self.active_instances[instance_id] = instance

        # Check concurrency limits
        if self.running_executions >= self.max_concurrent_executions:
            logger.info(f"Concurrency limit reached ({self.max_concurrent_executions}), queuing workflow")
            asyncio.create_task(self._queue_and_execute(instance))
        else:
            self.running_executions += 1
            asyncio.create_task(self._run_workflow(instance, workflow_spec))

        logger.info(f"Workflow execution initiated: {instance_id} for workflow {workflow_spec['id']}")
        return instance_id

    def _create_step(self, step_data: Dict) -> WorkflowStep:
        """Create WorkflowStep from step data"""
        return WorkflowStep(
            name=step_data.get('name', f'step_{len(step_data)}'),
            type=step_data.get('type', 'generic'),
            config=step_data.get('config', {}),
            timeout_seconds=step_data.get('timeout_seconds', 60),
            retry_config=step_data.get('retry_config', {
                'max_attempts': 3,
                'backoff_multiplier': 2
            })
        )

    async def _queue_and_execute(self, instance: WorkflowInstance):
        """Queue workflow for later execution when capacity is available"""
        try:
            while self.running_executions >= self.max_concurrent_executions:
                await asyncio.sleep(5)  # Check every 5 seconds

            # Execute when capacity becomes available
            workflow_spec = {'id': instance.workflow_id, 'steps': []}
            await self._run_workflow(instance, workflow_spec)
        except Exception as e:
            logger.error(f"Error in queued workflow execution: {e}")
            instance.status = 'failed'
            instance.logs.append({
                'timestamp': datetime.now().isoformat(),
                'level': 'error',
                'message': f'Queued workflow failed: {str(e)}'
            })

    async def _run_workflow(self, instance: WorkflowInstance, workflow_spec: Dict):
        """Internal method to run workflow steps"""
        try:
            instance.status = 'running'
            instance.logs.append({
                'timestamp': datetime.now().isoformat(),
                'level': 'info',
                'message': f'Starting workflow execution with {len(instance.steps)} steps'
            })

            # Execute each step
            for step_idx, step in enumerate(instance.steps):
                instance.current_step = step_idx

                # Execute step with comprehensive error handling
                success = await self._execute_step_with_retry(instance, step)

                if not success:
                    await self._handle_step_failure(instance, step, step_idx)
                    break

            # Workflow completed successfully
            instance.status = 'completed'
            instance.completed_at = datetime.now()
            instance.metrics['success_rate'] = 1.0

            instance.logs.append({
                'timestamp': datetime.now().isoformat(),
                'level': 'info',
                'message': 'Workflow completed successfully'
            })

        except Exception as e:
            instance.status = 'failed'
            instance.logs.append({
                'timestamp': datetime.now().isoformat(),
                'level': 'error',
                'message': f'Workflow execution failed: {str(e)}'
            })

        finally:
            # Update running count and move to completed instances
            self.running_executions = max(0, self.running_executions - 1)
            self.completed_instances[instance.id] = instance
            self.active_instances.pop(instance.id, None)

    async def _execute_step_with_retry(self, instance: WorkflowInstance, step: WorkflowStep) -> bool:
        """Execute workflow step with retry logic"""
        step_start_time = datetime.now()

        for attempt in range(step.retry_config.get('max_attempts', 3)):
            try:
                # Log step start
                step_start_timestamp = datetime.now().isoformat()
                instance.logs.append({
                    'timestamp': step_start_timestamp,
                    'level': 'info',
                    'message': f'Executing step: {step.name} (attempt {attempt + 1})',
                    'step_data': {'name': step.name, 'type': step.type}
                })

                # Execute the step based on its type
                result = await self._execute_step_internal(instance, step)

                # Record successful execution metrics
                step_duration = (datetime.now() - step_start_time).total_seconds()
                instance.metrics[f'step_{step.name}_duration'] = step_duration
                instance.metrics[f'step_{step.name}_attempts'] = attempt + 1

                # Success! Log completion
                instance.logs.append({
                    'timestamp': datetime.now().isoformat(),
                    'level': 'info',
                    'message': f'Step {step.name} completed successfully',
                    'duration_seconds': step_duration
                })

                return True

            except Exception as e:
                step_duration = (datetime.now() - step_start_time).total_seconds()
                instance.metrics[f'step_{step.name}_duration'] = step_duration
                instance.metrics[f'step_{step.name}_attempt_{attempt + 1}_error'] = str(e)

                # Log failure
                instance.logs.append({
                    'timestamp': datetime.now().isoformat(),
                    'level': 'warning' if attempt < step.retry_config.get('max_attempts', 3) - 1 else 'error',
                    'message': f'Step {step.name} failed on attempt {attempt + 1}: {str(e)}',
                    'duration_seconds': step_duration
                })

                # Wait before retry (exponential backoff)
                if attempt < step.retry_config.get('max_attempts', 3) - 1:
                    backoff_time = step.retry_config.get('backoff_multiplier', 2) ** attempt
                    await asyncio.sleep(backoff_time)

        # All retries exhausted
        step_duration = (datetime.now() - step_start_time).total_seconds()
        instance.metrics[f'step_{step.name}_final_attempt_failed'] = True
        instance.metrics[f'step_{step.name}_total_duration'] = step_duration

        return False

    async def _execute_step_internal(self, instance: WorkflowInstance, step: WorkflowStep) -> Any:
        """Internal step execution logic"""
        step_start = datetime.now()

        try:
            # Different execution strategies based on step type
            if step.type == 'api_call':
                result = await self._execute_api_call_step(instance, step)
            elif step.type == 'condition_check':
                result = await self._execute_condition_check_step(instance, step)
            elif step.type == 'data_transformation':
                result = await self._execute_data_transformation_step(instance, step)
            elif step.type == 'notification':
                result = await self._execute_notification_step(instance, step)
            elif step.type == 'file_operation':
                result = await self._execute_file_operation_step(instance, step)
            elif step.type == 'database_query':
                result = await self._execute_database_query_step(instance, step)
            else:
                raise ValueError(f"Unknown step type: {step.type}")

            step_duration = (datetime.now() - step_start).total_seconds()
            instance.metrics[f'step_{step.name}_execution_time'] = step_duration

            return result

        except asyncio.CancelledError:
            # Handle cancellation gracefully
            step_duration = (datetime.now() - step_start).total_seconds()
            instance.metrics[f'step_{step.name}_cancelled'] = True
            instance.metrics[f'step_{step.name}_cancellation_time'] = step_duration
            raise

        except Exception as e:
            step_duration = (datetime.now() - step_start).total_seconds()
            instance.metrics[f'step_{step.name}_error'] = str(e)
            instance.metrics[f'step_{step.name}_error_type'] = type(e).__name__
            instance.metrics[f'step_{step.name}_execution_time'] = step_duration

            # Re-raise to trigger retry logic
            raise

    async def _execute_api_call_step(self, instance: WorkflowInstance, step: WorkflowStep) -> Dict:
        """Execute API call step"""
        import aiohttp

        url = step.config.get('url')
        method = step.config.get('method', 'GET')
        headers = step.config.get('headers', {})
        data = step.config.get('data', {})

        if not url:
            raise ValueError("API step requires 'url' configuration")

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=step.timeout_seconds)) as session:
            async with session.request(method, url, headers=headers, json=data) as response:
                if response.status >= 400:
                    raise Exception(f"API call failed with status {response.status}: {await response.text()}")

                result = await response.json()
                return {'status': 'success', 'data': result, 'status_code': response.status}

    async def _execute_condition_check_step(self, instance: WorkflowInstance, step: WorkflowStep) -> bool:
        """Execute condition check step"""
        condition_config = step.config.get('condition', {})
        expression = condition_config.get('expression')

        if not expression:
            raise ValueError("Condition step requires 'expression' configuration")

        # In a real implementation, this would evaluate the expression safely
        # For now, we'll use a simple placeholder
        logger.debug(f"Evaluating condition: {expression}")

        # Placeholder evaluation - always returns True for demo
        # In production, use a safe expression evaluator like asteval or similar
        return True

    async def _execute_data_transformation_step(self, instance: WorkflowInstance, step: WorkflowStep) -> Dict:
        """Execute data transformation step"""
        transform_rules = step.config.get('transform_rules', [])

        if not transform_rules:
            raise ValueError("Data transformation step requires 'transform_rules' configuration")

        # Placeholder for data transformation logic
        # In production, this would apply actual transformation rules
        transformed_data = {
            'original_size': len(str(step.config.get('source_data', ''))),
            'rules_applied': len(transform_rules),
            'transformation_time': datetime.now().isoformat()
        }

        return transformed_data

    async def _execute_notification_step(self, instance: WorkflowInstance, step: WorkflowStep) -> Dict:
        """Execute notification step"""
        message = step.config.get('message', '')
        channels = step.config.get('channels', [])

        if not message:
            raise ValueError("Notification step requires 'message' configuration")

        results = {}

        for channel in channels:
            try:
                if channel == 'slack':
                    result = await self._send_slack_message(message)
                    results['slack'] = result
                elif channel == 'email':
                    result = await self._send_email_notification(message)
                    results['email'] = result
                elif channel == 'webhook':
                    result = await self._send_webhook_notification(message)
                    results['webhook'] = result
                else:
                    logger.warning(f"Unknown notification channel: {channel}")
                    results[channel] = {'status': 'unknown_channel'}

            except Exception as e:
                results[channel] = {'status': 'failed', 'error': str(e)}

        return results

    async def _execute_file_operation_step(self, instance: WorkflowInstance, step: WorkflowStep) -> Dict:
        """Execute file operation step"""
        operation = step.config.get('operation')
        filepath = step.config.get('filepath')
        content = step.config.get('content')

        if not operation or not filepath:
            raise ValueError("File operation step requires 'operation' and 'filepath' configuration")

        try:
            if operation == 'read':
                with open(filepath, 'r') as f:
                    result = f.read()
                return {'status': 'success', 'content': result, 'size_bytes': len(result)}
            elif operation == 'write':
                with open(filepath, 'w') as f:
                    f.write(content or '')
                return {'status': 'success', 'written_bytes': len(content or '')}
            elif operation == 'delete':
                import os
                os.remove(filepath)
                return {'status': 'success', 'deleted_file': filepath}
            else:
                raise ValueError(f"Unsupported file operation: {operation}")

        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {filepath}")
        except PermissionError:
            raise PermissionError(f"Permission denied: {filepath}")
        except Exception as e:
            raise Exception(f"File operation failed: {str(e)}")

    async def _execute_database_query_step(self, instance: WorkflowInstance, step: WorkflowStep) -> Dict:
        """Execute database query step"""
        query = step.config.get('query')
        connection_string = step.config.get('connection_string')

        if not query or not connection_string:
            raise ValueError("Database query step requires 'query' and 'connection_string' configuration")

        # Placeholder for actual database operations
        # In production, use proper database connection pooling and parameterized queries
        return {
            'status': 'success',
            'rows_affected': 0,
            'query_execution_time': 0.001,
            'connection_string_hash': hash(connection_string) % 1000000  # Placeholder
        }

    async def _send_slack_message(self, message: str) -> Dict:
        """Send Slack message"""
        # Placeholder implementation
        webhook_url = '***REMOVED***'

        payload = {'text': message}

        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload) as response:
                if response.status == 200:
                    return {'status': 'sent', 'platform': 'slack'}
                else:
                    raise Exception(f"Slack webhook failed: {response.status}")

    async def _send_email_notification(self, message: str) -> Dict:
        """Send email notification"""
        # Placeholder implementation
        return {'status': 'sent', 'platform': 'email', 'recipients': ['admin@example.com']}

    async def _send_webhook_notification(self, message: str) -> Dict:
        """Send webhook notification"""
        webhook_url = 'https://example.com/webhook'

        payload = {
            'event': 'workflow_notification',
            'message': message,
            'timestamp': datetime.now().isoformat()
        }

        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload) as response:
                if response.status == 200:
                    return {'status': 'sent', 'platform': 'webhook'}
                else:
                    raise Exception(f"Webhook failed: {response.status}")

    async def _handle_step_failure(self, instance: WorkflowInstance, step: WorkflowStep, step_idx: int):
        """Handle step failure with fallback strategies"""
        error_key = f"{instance.workflow_id}_{step_idx}"

        if error_key in self.error_handlers:
            handler = self.error_handlers[error_key]
            await handler(instance, step)
        else:
            # Default error handling
            await self._default_error_handler(instance, step)

    async def _default_error_handler(self, instance: WorkflowInstance, step: WorkflowStep):
        """Default error handling when no specific handler exists"""
        # Send alert to administrators
        await self._send_admin_alert(instance, step)

        # Add detailed error information
        instance.logs.append({
            'timestamp': datetime.now().isoformat(),
            'level': 'critical',
            'message': f'No error handler configured for step: {step.name}. Workflow execution stopped.'
        })

    async def _send_admin_alert(self, instance: WorkflowInstance, step: WorkflowStep):
        """Send alert to administrators about workflow failure"""
        alert_message = f"""
🚨 WORKFLOW EXECUTION ALERT

Workflow: {instance.workflow_id}
Instance ID: {instance.id}
Failed Step: {step.name} (Type: {step.type})
Time: {datetime.now().isoformat()}

Error Context:
{step.config}

Please investigate and take appropriate action.
"""

        # Try to send via multiple channels
        alert_results = {}

        try:
            alert_results['slack'] = await self._send_slack_message(alert_message)
        except Exception as e:
            alert_results['slack'] = {'status': 'failed', 'error': str(e)}

        try:
            alert_results['log'] = 'Alert logged to system logs'
        except Exception as e:
            alert_results['log'] = {'status': 'failed', 'error': str(e)}

        # Store alert results in instance metrics
        instance.metrics['admin_alert_sent'] = alert_results

    def register_error_handler(self, workflow_id: str, step_index: int, handler_func):
        """Register custom error handler for specific workflow step"""
        error_key = f"{workflow_id}_{step_index}"
        self.error_handlers[error_key] = handler_func
        logger.info(f"Registered custom error handler for {workflow_id}, step {step_index}")

    def get_instance_status(self, instance_id: str) -> Optional[Dict]:
        """Get status of a workflow instance"""
        instance = self.active_instances.get(instance_id) or self.completed_instances.get(instance_id)

        if not instance:
            return None

        return {
            'id': instance.id,
            'workflow_id': instance.workflow_id,
            'status': instance.status,
            'started_at': instance.started_at.isoformat(),
            'completed_at': instance.completed_at.isoformat() if instance.completed_at else None,
            'current_step': instance.current_step,
            'progress_percentage': round((instance.current_step / len(instance.steps)) * 100, 1) if instance.steps else 0,
            'logs_count': len(instance.logs),
            'metrics': instance.metrics
        }

    def cancel_workflow(self, instance_id: str) -> bool:
        """Cancel a running workflow"""
        instance = self.active_instances.get(instance_id)

        if not instance or instance.status != 'running':
            return False

        instance.status = 'cancelled'
        instance.completed_at = datetime.now()
        instance.metrics['cancellation_reason'] = 'user_requested'

        self.running_executions = max(0, self.running_executions - 1)
        self.completed_instances[instance_id] = instance
        self.active_instances.pop(instance_id)

        logger.info(f"Workflow cancelled: {instance_id}")
        return True

    def get_performance_summary(self) -> Dict:
        """Get summary of execution performance"""
        total_completed = len([i for i in self.completed_instances.values() if i.status == 'completed'])
        total_failed = len([i for i in self.completed_instances.values() if i.status == 'failed'])

        avg_execution_time = 0
        if self.completed_instances:
            completed_times = [
                (i.completed_at - i.started_at).total_seconds()
                for i in self.completed_instances.values()
                if i.status == 'completed' and i.completed_at
            ]
            avg_execution_time = sum(completed_times) / len(completed_times) if completed_times else 0

        return {
            'total_executions': len(self.completed_instances),
            'successful_executions': total_completed,
            'failed_executions': total_failed,
            'success_rate_percentage': round((total_completed / (total_completed + total_failed) * 100), 2) if (total_completed + total_failed) > 0 else 0,
            'average_execution_time_seconds': round(avg_execution_time, 2),
            'active_executions': len(self.active_instances),
            'concurrent_limit': self.max_concurrent_executions,
            'error_handlers_registered': len(self.error_handlers)
        }