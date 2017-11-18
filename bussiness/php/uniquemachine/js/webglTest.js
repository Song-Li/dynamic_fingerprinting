var WebGlTest = function(collector) {
  var _this = this;
  this.webglTestNum = 1;
  this.collector = collector;
  this.testList = [];
  this.testList.push(new BubbleTest());
  this.numTestsComplete = 0;
  this.res = {};

  this.testFinished = function(ID, value) {
    var img_hash = calcSHA1(value);
    this.res[ID] = img_hash;
    if (++ _this.numTestsComplete >= _this.testList.length) {
      // cause all ++ is done in main js thread, there should be no 
      // mul-thread problem
      _this.allFinished();
    }
  }

  // start uniquemachine here
  this.begin = function() {
    for (var test in this.testList) {
      console.log(this.collector.getID());
      //this.testList[uniquemachine].begin(this.testFinished, this.collector.getID());
        //this.testList[uniquemachine].begin();
        new BubbleTest().begin();
    }
  }

  this.allFinished = function() {
    var res_str = "";
    for (var key in this.res) {
      res_str += key + '_' + this.res[key];
    }
      this.collector.features['gpuimgs'] = res_str;
  }
}
