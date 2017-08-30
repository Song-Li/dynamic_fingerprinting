var AsyncTest = function(collector, cb) {
  var _this = this;
  this.cb = cb;
  this.webglTestNum = 1;
  this.collector = collector;
  this.testList = [];
  this.testList.push(new BubbleTest());
  this.numTestsComplete = 0;
  this.testFinished = function(ID, value) {
    collector.postData['gpuImgs'][ID] = value;
    window.open(value, '_blank');
    if (++ _this.numTestsComplete >= _this.testList.length) {
      // cause all ++ is done in main js thread, there should be no 
      // mul-thread problem
      _this.allFinished();
    }
  }

  // start test here
  this.begin = function() {
    for (var test in this.testList) {
      this.testList[test].begin(this.testFinished, collector.getID());
    }
  }

  this.allFinished = function() {
    _this.cb();
  }
}
