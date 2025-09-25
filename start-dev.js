const { spawn } = require('child_process');
const path = require('path');

console.log('='.repeat(60));
console.log('🚀 Kochi Metro Trainset Induction Planner - Dev Starter');
console.log('='.repeat(60));

// Function to start a process
function startProcess(command, cwd, name) {
  console.log(`\n🔧 Starting ${name}...`);
  
  const proc = spawn(command, {
    cwd: cwd,
    shell: true,
    stdio: 'inherit'
  });
  
  proc.on('error', (err) => {
    console.error(`❌ Error starting ${name}:`, err.message);
  });
  
  proc.on('close', (code) => {
    console.log(`\n${name} process exited with code ${code}`);
  });
  
  return proc;
}

// Start backend
const backendProcess = startProcess(
  'python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload',
  path.join(__dirname, 'backend'),
  'Backend Server'
);

// Start frontend
const frontendProcess = startProcess(
  'npm start',
  path.join(__dirname, 'frontend'),
  'Frontend Server'
);

console.log('\n' + '='.repeat(60));
console.log('✨ Both servers are now starting!');
console.log('   Backend:  http://localhost:8001');
console.log('   Frontend: http://localhost:3000');
console.log('\n📝 Press Ctrl+C to stop both servers');
console.log('='.repeat(60));

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.log('\n\n🛑 Shutting down servers...');
  if (backendProcess) backendProcess.kill();
  if (frontendProcess) frontendProcess.kill();
  process.exit(0);
});