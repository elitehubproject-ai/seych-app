const { PythonShell } = require('python-shell');

let options = {
  mode: 'text',
  pythonPath: 'python3',
  pythonOptions: ['-u'], // unbuffered output
  scriptPath: '.',
  args: []
};

let pyshell = new PythonShell('bot.py', options);

pyshell.on('message', function (message) {
  console.log(message);
});

pyshell.on('stderr', function (stderr) {
  console.error(stderr);
});

pyshell.end(function (err, code, signal) {
  if (err) throw err;
  console.log('Бот завершил работу');
});