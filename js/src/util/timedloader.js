class TimedLoader {
  /* credit: https://codepen.io/averzea/pen/PrLeaV */
  constructor(duration, showPercentage = false) {
    const self = this;
    self.duration = duration;
    self.showPercentage = showPercentage;

    this.newDegrees = 0;
  }

  #init() {
    const spinner = document.getElementById('timed-loader');
    const ctx = spinner.getContext('2d');
    const width = spinner.width;
    const height = spinner.height;
    const color = 'turquoise';
    const bgcolor = '#222';
    let text;

    ctx.clearRect(0, 0, width, height);

    ctx.beginPath();
    ctx.strokeStyle = bgcolor;
    ctx.lineWidth = 30;
    ctx.arc(width / 2, width / 2, 100, 0, Math.PI * 2, false);
    ctx.stroke();
    const radians = this.degrees * Math.PI / 180;

    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineWidth = 30;
    ctx.arc(
        width / 2, height / 2,
        100, 0 - 90 * Math.PI / 180,
        radians - 90 * Math.PI / 180,
        false,
    );
    ctx.stroke();
    ctx.fillStyle = color;

    if (self.showPercentage) {
      ctx.font = '50px arial';
      text = Math.floor(this.degrees / 360 * 100) + '%';
      const textWidth = ctx.measureText(text).width;
      ctx.fillText(text, width / 2 - textWidth / 2, height / 2 + 15);
    }
  }

  #draw() {
    if (typeof this.animationLoop != undefined) {
      clearInterval(this.animationLoop);
    }

    this.newDegrees = 360;
    this.animationLoop = setInterval(
        this.#animateTo.bind(this),
        this.duration / (this.newDegrees - this.degrees),
    );
  }

  #animateTo() {
    if (this.degrees == this.newDegrees) {
      clearInterval(this.animationLoop);
    } else if (this.degrees < this.newDegrees) {
      this.degrees++;
    } else {
      this.degrees--;
    }
    this.#init();
  }

  start() {
    this.degrees = 0;
    this.#draw();
  }
}

export default TimedLoader;
