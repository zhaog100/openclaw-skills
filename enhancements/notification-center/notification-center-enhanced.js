/**
 * Notification Center v3.1 - Enhanced with grouping, inline actions, history page
 * 
 * Enhancements for INDIGOAZUL/la-tanda-web #268
 * - Type-based grouping
 * - Inline actions (approve/reject/dismiss)
 * - History page with pagination
 * - Mark-all-read functionality
 */

class EnhancedNotificationCenter {
  constructor(config = {}) {
    this.container = config.container || '#notification-center';
    this.apiEndpoint = config.apiEndpoint || '/api/notifications';
    this.grouping = config.grouping !== false;
    this.inlineActions = config.inlineActions !== false;
    this.historyPage = config.historyPage !== false;
    this.markAllRead = config.markAllRead !== false;
    
    this.notifications = [];
    this.groups = {};
    this.currentPage = 1;
    this.pageSize = 20;
    
    this.init();
  }

  async init() {
    await this.loadNotifications();
    this.render();
    this.bindEvents();
  }

  // Group notifications by type
  groupByType() {
    this.groups = {
      transactions: [],
      governance: [],
      staking: [],
      system: [],
      other: []
    };

    this.notifications.forEach(n => {
      const type = n.type || 'other';
      if (this.groups[type]) {
        this.groups[type].push(n);
      } else {
        this.groups.other.push(n);
      }
    });

    return this.groups;
  }

  // Render grouped notifications
  renderGrouped() {
    const groups = this.groupByType();
    const container = document.getElementById(this.container);
    
    container.innerHTML = `
      <div class="notification-center-enhanced">
        ${this.markAllRead ? this.renderMarkAllRead() : ''}
        ${this.renderGroupTabs(groups)}
        ${this.renderGroupContent(groups)}
        ${this.historyPage ? this.renderHistoryPage() : ''}
      </div>
    `;
  }

  // Render group tabs
  renderGroupTabs(groups) {
    const counts = Object.entries(groups).map(([type, items]) => ({
      type,
      count: items.length,
      unread: items.filter(n => !n.read).length
    }));

    return `
      <div class="notification-tabs">
        ${counts.map(g => `
          <button class="tab ${g.type === 'transactions' ? 'active' : ''}" 
                  data-group="${g.type}">
            ${this.getGroupIcon(g.type)} ${this.getGroupName(g.type)}
            <span class="badge">${g.count}</span>
            ${g.unread > 0 ? `<span class="unread-badge">${g.unread}</span>` : ''}
          </button>
        `).join('')}
      </div>
    `;
  }

  // Render notification group content
  renderGroupContent(groups) {
    return `
      <div class="notification-groups">
        ${Object.entries(groups).map(([type, items]) => `
          <div class="notification-group" data-group="${type}" 
               style="display: ${type === 'transactions' ? 'block' : 'none'}">
            ${items.length === 0 ? '<p class="empty-state">No notifications</p>' : 
              items.map(n => this.renderNotification(n)).join('')}
          </div>
        `).join('')}
      </div>
    `;
  }

  // Render single notification with inline actions
  renderNotification(notification) {
    const actions = this.inlineActions ? `
      <div class="notification-actions">
        <button class="action-btn approve" data-id="${notification.id}" title="Approve">✓</button>
        <button class="action-btn reject" data-id="${notification.id}" title="Reject">✗</button>
        <button class="action-btn dismiss" data-id="${notification.id}" title="Dismiss">—</button>
      </div>
    ` : '';

    return `
      <div class="notification-item ${notification.read ? 'read' : 'unread'}" 
           data-id="${notification.id}">
        <div class="notification-header">
          <span class="notification-type ${notification.type}">
            ${this.getTypeIcon(notification.type)}
          </span>
          <span class="notification-title">${notification.title}</span>
          <span class="notification-time">${this.formatTime(notification.created_at)}</span>
        </div>
        <div class="notification-body">${notification.body}</div>
        ${actions}
      </div>
    `;
  }

  // Render mark-all-read button
  renderMarkAllRead() {
    return `
      <div class="notification-header-actions">
        <button id="mark-all-read" class="btn-primary">
          Mark all as read
        </button>
      </div>
    `;
  }

  // Render history page
  renderHistoryPage() {
    const totalPages = Math.ceil(this.notifications.length / this.pageSize);
    
    return `
      <div class="notification-history">
        <h3>History</h3>
        <div class="pagination">
          <button class="page-btn" data-page="${this.currentPage - 1}" 
                  ${this.currentPage <= 1 ? 'disabled' : ''}>
            ← Previous
          </button>
          <span class="page-info">Page ${this.currentPage} of ${totalPages}</span>
          <button class="page-btn" data-page="${this.currentPage + 1}" 
                  ${this.currentPage >= totalPages ? 'disabled' : ''}>
            Next →
          </button>
        </div>
        <div class="history-list">
          ${this.getPaginatedNotifications().map(n => 
            this.renderNotification(n)
          ).join('')}
        </div>
      </div>
    `;
  }

  // Get paginated notifications
  getPaginatedNotifications() {
    const start = (this.currentPage - 1) * this.pageSize;
    const end = start + this.pageSize;
    return this.notifications.slice(start, end);
  }

  // Event bindings
  bindEvents() {
    // Tab switching
    document.querySelectorAll('.notification-tabs .tab').forEach(tab => {
      tab.addEventListener('click', (e) => {
        const group = e.currentTarget.dataset.group;
        this.switchGroup(group);
      });
    });

    // Inline actions
    document.querySelectorAll('.action-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = e.currentTarget.dataset.id;
        const action = e.currentTarget.classList.contains('approve') ? 'approve' :
                       e.currentTarget.classList.contains('reject') ? 'reject' : 'dismiss';
        this.handleAction(id, action);
      });
    });

    // Mark all read
    const markAllBtn = document.getElementById('mark-all-read');
    if (markAllBtn) {
      markAllBtn.addEventListener('click', () => this.markAllAsRead());
    }

    // Pagination
    document.querySelectorAll('.page-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const page = parseInt(e.currentTarget.dataset.page);
        if (page > 0) {
          this.currentPage = page;
          this.render();
        }
      });
    });
  }

  // Switch notification group
  switchGroup(group) {
    document.querySelectorAll('.notification-tabs .tab').forEach(t => t.classList.remove('active'));
    document.querySelector(`.tab[data-group="${group}"]`).classList.add('active');
    
    document.querySelectorAll('.notification-group').forEach(g => g.style.display = 'none');
    document.querySelector(`.notification-group[data-group="${group}"]`).style.display = 'block';
  }

  // Handle notification action
  async handleAction(id, action) {
    try {
      const response = await fetch(`${this.apiEndpoint}/${id}/${action}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        this.notifications = this.notifications.filter(n => n.id !== id);
        this.render();
      }
    } catch (error) {
      console.error(`Failed to ${action} notification ${id}:`, error);
    }
  }

  // Mark all as read
  async markAllAsRead() {
    try {
      const response = await fetch(`${this.apiEndpoint}/mark-all-read`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        this.notifications.forEach(n => n.read = true);
        this.render();
      }
    } catch (error) {
      console.error('Failed to mark all as read:', error);
    }
  }

  // Helper methods
  getGroupIcon(type) {
    const icons = {
      transactions: '💰',
      governance: '🏛️',
      staking: '📊',
      system: '⚙️',
      other: '📋'
    };
    return icons[type] || '📋';
  }

  getGroupName(type) {
    const names = {
      transactions: 'Transactions',
      governance: 'Governance',
      staking: 'Staking',
      system: 'System',
      other: 'Other'
    };
    return names[type] || 'Other';
  }

  getTypeIcon(type) {
    const icons = {
      transaction: '💰',
      governance_vote: '🗳️',
      governance_proposal: '📜',
      staking_reward: '🎁',
      staking_delegation: '📤',
      system_alert: '⚠️',
      system_update: '🔄'
    };
    return icons[type] || '📋';
  }

  formatTime(date) {
    const d = new Date(date);
    const now = new Date();
    const diff = now - d;
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return d.toLocaleDateString();
  }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
  module.exports = EnhancedNotificationCenter;
}
