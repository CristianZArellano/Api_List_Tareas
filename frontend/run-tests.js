#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');

// Configuración para los tests
const testConfig = {
  // Ejecutar tests en modo watch por defecto
  watch: process.argv.includes('--watch') || process.argv.includes('-w'),
  // Ejecutar tests con coverage
  coverage: process.argv.includes('--coverage') || process.argv.includes('-c'),
  // Ejecutar tests específicos
  testNamePattern: process.argv.find(arg => arg.startsWith('--testNamePattern='))?.split('=')[1],
  // Ejecutar tests en modo verbose
  verbose: process.argv.includes('--verbose') || process.argv.includes('-v'),
  // Ejecutar tests en modo silent
  silent: process.argv.includes('--silent') || process.argv.includes('-s'),
};

// Construir comando de Jest
let jestCommand = 'npx';
let jestArgs = ['jest'];

// Agregar argumentos según la configuración
if (testConfig.watch) {
  jestArgs.push('--watch');
}

if (testConfig.coverage) {
  jestArgs.push('--coverage');
  jestArgs.push('--coverageReporters=text');
  jestArgs.push('--coverageReporters=lcov');
  jestArgs.push('--coverageDirectory=coverage');
}

if (testConfig.testNamePattern) {
  jestArgs.push('--testNamePattern', testConfig.testNamePattern);
}

if (testConfig.verbose) {
  jestArgs.push('--verbose');
}

if (testConfig.silent) {
  jestArgs.push('--silent');
}

// Configuración adicional de Jest
jestArgs.push('--testEnvironment=jsdom');
jestArgs.push('--setupFilesAfterEnv=./src/setupTests.js');

// Colores para la salida
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
};

console.log(`${colors.cyan}${colors.bright}🚀 Ejecutando tests del frontend...${colors.reset}`);
console.log(`${colors.blue}Comando: ${jestCommand} ${jestArgs.join(' ')}${colors.reset}\n`);

// Ejecutar Jest
const jestProcess = spawn(jestCommand, jestArgs, {
  stdio: 'inherit',
  shell: true,
  cwd: __dirname,
});

jestProcess.on('close', (code) => {
  if (code === 0) {
    console.log(`\n${colors.green}${colors.bright}✅ Todos los tests pasaron exitosamente!${colors.reset}`);
  } else {
    console.log(`\n${colors.red}${colors.bright}❌ Algunos tests fallaron (código: ${code})${colors.reset}`);
    process.exit(code);
  }
});

jestProcess.on('error', (error) => {
  console.error(`${colors.red}Error al ejecutar Jest:${colors.reset}`, error);
  process.exit(1);
});

// Manejar señales de terminación
process.on('SIGINT', () => {
  console.log(`\n${colors.yellow}Deteniendo tests...${colors.reset}`);
  jestProcess.kill('SIGINT');
});

process.on('SIGTERM', () => {
  console.log(`\n${colors.yellow}Deteniendo tests...${colors.reset}`);
  jestProcess.kill('SIGTERM');
}); 