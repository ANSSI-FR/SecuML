function isProbability(p) {
    return !isNaN(p) && p > 0 && p < 1;
}

function getRandomInt(min, max) {
  return Math.floor(Math.random() * (max - min)) + min;
}

function isInList(elem, list) {
  for (i in list) {
      l = list[i];
      if (l == elem) {
          return true;
      }
  }
  return false;
}
