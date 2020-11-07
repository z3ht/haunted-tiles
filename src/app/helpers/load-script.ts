
/// loadScript() takes either es6 module source code as a string or
/// a url to some source code.  Returns the default export or the module
/// if no default export is provided
export async function loadScript<T>(src: string): Promise<T> {
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
  const module = await import(/* webpackIgnore: true */ `data:text/javascript;charset=utf-8,${code}`);
  return (module.default || module) as T;
}
