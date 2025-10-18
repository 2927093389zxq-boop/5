// 验证数据管道修复的简单测试脚本
const fs = require('fs');
const path = require('path');

console.log('开始验证数据管道修复...');

// 检查目录结构
const requiredDirs = [
  'data/raw',
  'data/processed', 
  'data/seeds',
  'data/schema',
  'data/metadata',
  'data/config'
];

console.log('\n检查目录结构:');
let dirsValid = true;
for (const dir of requiredDirs) {
  const fullPath = path.join(__dirname, '..', dir);
  if (fs.existsSync(fullPath) && fs.statSync(fullPath).isDirectory()) {
    console.log(`✓ ${dir} 存在`);
  } else {
    console.log(`✗ ${dir} 不存在或不是目录`);
    dirsValid = false;
  }
}

// 检查配置文件
console.log('\n检查配置文件:');
let configValid = false;
const configPath = path.join(__dirname, '..', 'data', 'config', 'source.config.json');
if (fs.existsSync(configPath)) {
  try {
    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    console.log('✓ source.config.json 存在且格式正确');
    console.log(`  - 定义了 ${config.sources ? config.sources.length : 0} 个数据源`);
    configValid = true;
  } catch (error) {
    console.log(`✗ source.config.json 解析错误: ${error.message}`);
  }
} else {
  console.log('✗ source.config.json 不存在');
}

// 检查脚本文件
console.log('\n检查脚本文件:');
const scriptFiles = [
  'fetch_source.mjs',
  'process_data.mjs',
  'generate_seeds.mjs',
  'test_pipeline.mjs'
];

let scriptsExist = true;
for (const script of scriptFiles) {
  const scriptPath = path.join(__dirname, script);
  if (fs.existsSync(scriptPath)) {
    console.log(`✓ ${script} 存在`);
  } else {
    console.log(`⚠ ${script} 不存在`);
    scriptsExist = false;
  }
}

// 检查工作流文件
console.log('\n检查工作流文件:');
const workflowPath = path.join(__dirname, '..', '.github', 'workflows', 'data-pipeline.yml');
if (fs.existsSync(workflowPath)) {
  console.log('✓ data-pipeline.yml 存在');
  // 检查是否包含改进的错误处理
  const workflowContent = fs.readFileSync(workflowPath, 'utf8');
  if (workflowContent.includes('mkdir -p data/raw') && 
      workflowContent.includes('if [ -f "data/config/source.config.json" ]') &&
      workflowContent.includes('try {')) {
    console.log('✓ 工作流文件包含改进的错误处理逻辑');
  } else {
    console.log('✗ 工作流文件缺少预期的改进');
  }
}

// 总结
console.log('\n=== 验证总结 ===');
if (dirsValid && configValid) {
  console.log('✅ 数据管道环境已准备就绪，修复成功！');
  console.log('建议: 在GitHub上触发工作流测试，确保CI流程正常运行。');
} else {
  console.log('⚠️  部分检查未通过，建议进一步检查和修复。');
}