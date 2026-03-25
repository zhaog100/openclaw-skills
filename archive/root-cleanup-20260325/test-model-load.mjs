import { getLlama, resolveModelFile } from 'node-llama-cpp';
import path from 'path';

async function testModelLoad() {
  console.log('Starting model load test...');
  console.log('QMD_FORCE_CPU:', process.env.QMD_FORCE_CPU);

  try {
    // Force CPU mode
    const llama = await getLlama({ gpu: false, logLevel: 'debug' });
    console.log('Llama instance created successfully');

    // Try to load the model
    const modelPath = 'C:\\Users\\zhaog\\.cache\\qmd\\models\\embeddinggemma-300M-Q8_0.gguf';
    console.log('Loading model from:', modelPath);

    const model = await llama.loadModel({ modelPath });
    console.log('Model loaded successfully!');

    // Clean up
    await model.dispose();
    console.log('Test completed successfully');
  } catch (error) {
    console.error('Error during model load test:');
    console.error('Error message:', error.message);
    console.error('Error stack:', error.stack);
    process.exit(1);
  }
}

testModelLoad();
