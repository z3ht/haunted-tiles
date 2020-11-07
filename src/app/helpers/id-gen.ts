export function* MakeIdGen(seed = 0) {
  for(let i = seed;;i++) yield i;
}
