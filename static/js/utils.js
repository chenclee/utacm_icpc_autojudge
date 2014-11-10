function pad (n, width, z) {
  z = z || '0';
  n = n + '';
  return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
}

function moment (time) {
  hours = parseInt(parseInt(time / 60) / 60);
  minutes = parseInt(time / 60) % 60;
  seconds = time % 60;
  return pad(hours, 2) + ":" + pad(minutes, 2) + ":" + pad(seconds, 2);
}
