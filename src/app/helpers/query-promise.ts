export enum PromiseState {
  Rejected,
  Pending,
  Resolved,
}

type ResolveFn<T> = (value?: T | PromiseLike<T>) => void;
type RejectFn = (reason: any) => void;
type ExecutorFn<T> = (resolve: ResolveFn<T>, reject: RejectFn) => void;

export class QueryablePromise<T> extends Promise<T> {
  private _state: PromiseState = PromiseState.Pending;
  get state(): PromiseState { return this._state; }

  constructor(executor: ExecutorFn<T>) {
    super((resolve, reject) => {
      const resolveFn: ResolveFn<T> = value => {
        this._state = PromiseState.Resolved;
        resolve(value);
      };

      const rejectFn: RejectFn = reason => {
        this._state = PromiseState.Rejected;
        reject(reason);
      };

      executor(resolveFn, rejectFn);
    });
  }
}
