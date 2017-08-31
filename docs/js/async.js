var AsyncTest = function(collector, cb) {
  var _this = this;
  this.cb = cb;
  this.webglTestNum = 1;
  this.collector = collector;
  this.testList = [];
  this.testList.push(new BubbleTest());
  this.numTestsComplete = 0;
  this.testFinished = function(ID, value) {
    var img_hash = calcSHA1(value);
    collector.postData['gpuImgs'][ID] = img_hash;
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
    collector.asyncFinished();
  }
}
