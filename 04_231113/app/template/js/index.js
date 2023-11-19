let container = document.getElementById("container");
let context = container.getContext("2d");

const WIDTH_CONTAINER = 1024;
const HEIGHT_CONTAINER = 720;

container.width = WIDTH_CONTAINER;
container.height = HEIGHT_CONTAINER;
context.strokeRect(24, 24, 1, HEIGHT_CONTAINER - 36);
context.strokeRect(12, HEIGHT_CONTAINER - 24, WIDTH_CONTAINER - 36, 1);

const TICK_MAX_WIDTH = 100;
const TICK_MIN_WIDTH = 25;

const drawTick = (x, y, width, direction) => {
  let color = direction === 1 ? "green" : "red";

  context.fillStyle = color;
  context.beginPath();
  context.roundRect(
    x,
    y,
    width,
    10,
    5
  );
  context.fill();
};

const drawDirection = (x, _array, direction) => {
  let max_amount = 23;
  _array.forEach((el) => {
    max_amount = max_amount < el[1] ? el[1] : max_amount;
  });

  _array.forEach((el) => {
    let _width = (el[1] / max_amount) * TICK_MAX_WIDTH;
    _width = _width < TICK_MIN_WIDTH ? TICK_MIN_WIDTH : _width;

    let _position = x - _width / 2;

    drawTick(_position, el[0], _width, direction);
  });
};

bids = [
  [100, 15],
  [115, 10],
  [130, 20],
];

asks = [
  [85, 14],
  [70, 23],
  [55, 21],
  [40, 10],
];

drawDirection(136, bids, 1);
drawDirection(136, asks, 2);

bids = [
  [115, 20],
  [130, 18],
  [145, 18],
  [160, 17],
];

asks = [
  [100, 3],
  [85, 14],
  [70, 23],
  [55, 21],
  [40, 10],
];
drawDirection(248, bids, 1);
drawDirection(248, asks, 2);
