import { MakeIdGen } from './id-gen';

// const untrustedFn = new Function(\`${code}; return main(...arguments);\`);

function createWebWorkerSource(code: string, id: any, timeout = 2000) {
  const workerScript = `
  const __script_id = '${id.replace(/[^a-z0-9]/gmi, "")}';
  const __ScriptState = Object.freeze({
    Uninitialized: 'uninitialized',
    Initializing: 'initializing',
    Ready: 'ready',
    Busy: 'busy',
    Error: 'error',
  });
  let __script_state = __ScriptState.Uninitialized;

  // helper function for debugging
  function log(...args) {
    const a = [\`[SCRIPT:${'${__script_id}'}]\`, ...args];
    console.log(...a);
  }

  // effectively this anonymous function is "main", but it allows for async/await calls.
  (async function(){

    // __initialize() is used to import the "remote" script
    function __initialize() {
      __script_state = __ScriptState.Initializing;
      return new Promise((resolve, reject) => {
        // assume code we are loading has a main() function

        try {
          importScripts(URL.createObjectURL(new Blob([\`
          ${code}
          \`], { type: 'text/javascript' })));
          const untrustedFn = main;
          __script_state = __ScriptState.Ready;
          resolve(untrustedFn);
        } catch (error) {

          __script_state = __ScriptState.Error;
          reject(error);
        }
      });
    }

    // call the __initialize function to preload the user script
    // and catch any compilation error
    __initialize()
    .then(user_fn => {

      // wrap the user script in an internal function
      // so that we can manage the state flag
      return async (...args) => {
        __script_state = __ScriptState.Busy;
        const result = await Promise.resolve(user_fn(...args));
        __script_state = __ScriptState.Ready;
        return result;
      };
    }).then(user_fn => {

      // register a handler to respond to requests to run
      // the remote untrusted code
      onmessage = async (evt) => {

        // only run the code if we are already not processing code
        if (__script_state === __ScriptState.Ready) {
          const args = evt.data;
          try {

            // run the untrusted code in a promise in case it's asynchronous
            const result = await Promise.race([
              Promise.resolve(user_fn(...args)),
              new Promise((resolve, reject) => {
                setTimeout(() => {
                  // this.kill();
                  reject('timeout');
                }, ${timeout})
              }),
            ]);
            // const result = await Promise.resolve(user_fn(...args));
            self.postMessage({result});
          } catch (error) {

            // untrusted code choked, report the error!
            console.warn('untrusted code error', error);
            self.postMessage({error: error.toString()});
          }
          return;
        } else {
          self.postMessage({error: \`Script not ready.  Current state = ${'${__script_state}'}\`});
        }
      };

      // if if the initialization was okay, and the untrusted
      // code was successfully loaded, then let the host know
      log('successfully loaded user script');
      self.postMessage({result: 'success'});
    }).catch(error => {

      // if we are here, then the untrusted code failed to import
      __script_state = __ScriptState.Error;
      log('Failed to initialize user script.', error);
      self.postMessage({error: \`${'${error}'}\`});
    });
  })();
  `;


  const blob = new Blob([workerScript], {type: 'application/javascript'});
  return URL.createObjectURL(blob);
}

export interface ISandbox<Result> {
  kill(): void;
  evalAsync(args: any[], timeout?: number): Promise<Result>;
}

const idGen = MakeIdGen();

class Sandbox<Result> {
  private readonly id: string;
  private _worker: Worker = null;
  private get worker() {


    return this._worker;
  }

  constructor(identifier: string, private untrustedCode: string) {
    this.id = `${identifier}-${idGen.next().value}`;
  }

  initialize() {
    if (this._worker === null) {
      return new Promise((resolve, reject) => {
        const urlObject = createWebWorkerSource(this.untrustedCode, this.id, 2000);
        const opts: WorkerOptions = {
          // type: 'module'
        }
        this._worker = new Worker(urlObject, opts);
        this._worker.onmessage = evt => {
          const {error, result} = evt.data as {error?: any, result?: string};
          if (error) {
            return reject(error);
          } else {
            return resolve(result);
          }
        }
      });
    } else {
      return Promise.resolve();
    }
  }

  kill() {
    if (this._worker) {
      this._worker.terminate();
      this._worker = null;
    }
  }

  evalAsync(input: any[], timeout = 2000): Promise<Result> {
    const worker = this.worker;
    return new Promise((resolve, reject) => {
      worker.onmessage = evt => {
        const {error, result} = evt.data as {error?: any, result?: Result};
        if (error) {
          reject(error);
        } else {
          resolve(result);
        }
      };

      worker.onerror = err => {
        reject(err);
      }

      worker.postMessage(input);
    });
  }

  private log(...args) {
    const parts = [`[HOST:${this.id}]:`, ...args];
    console.log(...parts);
  }
}

export async function createSandboxAsync<T>(id: string, src: string): Promise<ISandbox<T>> {
  let isUrl = true;

  try {
    new URL(src);
  } catch (_) {
    isUrl = false;
  }

  let code = src;
  if (isUrl) {
    const res = await fetch(src);
    code = await res.text();
  }

  const sandbox = new Sandbox<T>(id, code);
  await sandbox.initialize();
  return sandbox;
}
