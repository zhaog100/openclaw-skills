#!/usr/bin/env node

const { loadConfig } = require('./lib');

const config = loadConfig();

function analyzeFileType(filePath) {
  if (!filePath) {
    return { hasFile: false, fileType: null, model: null };
  }

  const ext = require('path').extname(filePath).toLowerCase();
  const fileTypes = config.file_type_mapping || {};

  let fileType = 'main';
  for (const [type, extensions] of Object.entries(fileTypes)) {
    if (extensions.includes(ext)) {
      fileType = type;
      break;
    }
  }

  const modelMap = {
    vision: config.models.vision?.id,
    coding: config.models.coding?.id,
    complex: config.models.complex?.id,
    main: config.models.main?.id
  };

  return {
    hasFile: true,
    fileType,
    fileExtension: ext,
    model: modelMap[fileType] || config.models.main?.id
  };
}

if (require.main === module) {
  const filePath = process.argv[2];
  const result = analyzeFileType(filePath);
  console.log(JSON.stringify(result, null, 2));
}

module.exports = { analyzeFileType };
