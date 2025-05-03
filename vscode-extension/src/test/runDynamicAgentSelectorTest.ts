import Mocha from 'mocha';
import * as path from 'path';

async function run(): Promise<void> {
  // Create the mocha test
  const mocha = new Mocha({
    ui: 'bdd',
    color: true
  });

  // Add the test file
  mocha.addFile(path.resolve(__dirname, 'dynamicAgentSelectorTest.js'));

  // Run the tests
  return new Promise<void>((resolve, reject) => {
    mocha.run((failures: number) => {
      if (failures > 0) {
        reject(new Error(`${failures} tests failed.`));
      } else {
        resolve();
      }
    });
  });
}

// Run the tests
run().catch(err => {
  console.error('Test run failed:', err);
  process.exit(1);
});
