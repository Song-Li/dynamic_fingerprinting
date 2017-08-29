ip_address = "lab.songli.io/uniquemachine/";
var Collector = function() {
  this.finalized = false;
  this.postData = {
    flashFonts: "No Flash",
    fonts: "",
    WebGL: false,
    inc: "Undefined",
    gpu: "Undefined",
    timezone: "Undefined",
    resolution: "Undefined",
    plugins: "Undefined",
    cookie: "Undefined",
    localstorage: "Undefined",
    manufacturer: "Undefined",
    gpuImgs: {},
    adBlock: "Undefined",
    cpu_cores: "Undefined", 
    canvas_test: "Undefined", 
    audio: "Undefined",
    langsDetected: [],
    video: [],
    cc_audio: [],
    hybrid_audio: []
  };

  //get the usable fonts by flash
  this.flashFontsDetection = function(_this) {
    if (typeof window.swfobject === "undefined") {
      console.log("No flash available");
      return "";    
    }
    if(!swfobject.hasFlashPlayerVersion("9.0.0")){
      console.log("Insufficient flash version: need at least 9.0.0");
      return "";
    }
    var hiddenCallback = "___fp_swf_loaded";
    window[hiddenCallback] = function(fonts) {
      //this loop is used to replace , in fonts
      for (var i = 0;i < fonts.length;++ i) {
        fonts[i] = fonts[i].replace(/,/g , " ");
        fonts[i] = fonts[i].replace(/[^\x00-\xFF]/g, "?");
      }
      _this.postData['flashFonts'] = fonts.join("_");
      _this.flashFontsDetectionFinished();
    };
    var id = "flashfontfp";
    var node = document.createElement("div");
    node.setAttribute("id", id);
    document.body.appendChild(node);
    var flashvars = { onReady: hiddenCallback};
    var flashparams = { allowScriptAccess: "always", menu: "false" };
    swfobject.embedSWF("static/FontList.swf", id, "1", "1", "9.0.0", false, flashvars, flashparams, {});    
  }

  // get the basic info of audio card
  this.audioFingerPrinting = function() {
    var finished = false;
    try{
      var audioCtx = new (window.AudioContext || window.webkitAudioContext),
      oscillator = audioCtx.createOscillator(),
      analyser = audioCtx.createAnalyser(),
      gainNode = audioCtx.createGain(),
      scriptProcessor = audioCtx.createScriptProcessor(4096,1,1);
      var destination = audioCtx.destination;
      return (audioCtx.sampleRate).toString() + '_' + destination.maxChannelCount + "_" + destination.numberOfInputs + '_' + destination.numberOfOutputs + '_' + destination.channelCount + '_' + destination.channelCountMode + '_' + destination.channelInterpretation;
    }
    catch (e) {
      return "not supported";
    }
  }

  // get the screen resolution
  this.getResolution = function() {
    var zoom_level = detectZoom.device();
    var fixed_width = window.screen.width * zoom_level;
    var fixed_height = window.screen.height * zoom_level;
    var res = Math.round(fixed_width) + '_' + Math.round(fixed_height) + '_' + zoom_level + '_' + window.screen.width+"_"+window.screen.height+"_"+window.screen.colorDepth+"_"+window.screen.availWidth + "_" + window.screen.availHeight + "_" + window.screen.left + '_' + window.screen.top + '_' + window.screen.availLeft + "_" + window.screen.availTop + "_" + window.innerWidth + "_" + window.outerWidth + "_" + detectZoom.zoom();
    return res;
  }


  // get the list of plugins
  this.getPlugins = function() {
    var plgs_len = navigator.plugins.length;
    var plugins = [];
    for(var i = 0;i < plgs_len;i ++) {
      plugins.push(navigator.plugins[i].name);
    }
    plugins.sort();
    var plgs = plugins.join("~");
    plgs = plgs.replace(/[^a-zA-Z~ ]/g, "");
    return plgs;
  };

  // check the support of local storage
  this.checkLocalStorage = function() {
    try {
      localStorage.setItem('test', 'test');
      localStorage.removeItem('test');
      return true;
    } catch(e) {
      return false;
    }
  };

  // get the number of CPU cores
  this.getCPUCores = function() {
    if(!navigator.hardwareConcurrency)
      return "-1"
    else
      return navigator.hardwareConcurrency;
  };

  // check the support of WebGL
  this.getWebGL = function() {
    canvas = getCanvas('tmp_canvas');
    var gl = getGL(canvas);
    return gl;
  }

  // get the inc info
  this.getInc = function(gl) {
    var debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
    if (debugInfo) return gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
    return "No Debug Info";
  }

  // get the GPU info
  this.getGpu = function(gl) {
    var debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
    if (debugInfo) return gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
    return "No Debug Info";
  }

  // get the canvas test information

  var CanvasTest = function() {
    canvasData = "Not supported";
    canvas = $("<canvas height='60' width='400'></canvas>")[0];
    canvasContext = canvas.getContext("2d");
    canvas.style.display = "inline";
    canvasContext.textBaseline = "alphabetic";
    canvasContext.fillStyle = "#f60";
    canvasContext.fillRect(125, 1, 62, 20);
    canvasContext.fillStyle = "#069";
    canvasContext.font = "11pt no-real-font-123";
    canvasContext.fillText("Cwm fjordbank glyphs vext quiz, \ud83d\ude03", 2, 15);
    canvasContext.fillStyle = "rgba(102, 204, 0, 0.7)";
    canvasContext.font = "18pt Arial";
    canvasContext.fillText("Cwm fjordbank glyphs vext quiz, \ud83d\ude03", 4, 45);
    return canvas;
  }

  this.finished = false;

  //INSERTION OF AUDIOFINGERPRINT CODE
  // Performs fingerprint as found in https://www.cdn-net.com/cc.js
  var run_cc_fp = function(_this) {
    var cc_output = [];
    var audioCtx = new(window.AudioContext || window.webkitAudioContext),
    oscillator = audioCtx.createOscillator(),
    analyser = audioCtx.createAnalyser(),
    gain = audioCtx.createGain(),
    scriptProcessor = audioCtx.createScriptProcessor(4096, 1, 1);


    gain.gain.value = 0; // Disable volume
    oscillator.type = "triangle"; // Set oscillator to output triangle wave
    oscillator.connect(analyser); // Connect oscillator output to analyser input
    analyser.connect(scriptProcessor); // Connect analyser output to scriptProcessor input
    scriptProcessor.connect(gain); // Connect scriptProcessor output to gain input
    gain.connect(audioCtx.destination); // Connect gain output to audiocontext destination

    var results = [];
    scriptProcessor.onaudioprocess = function (bins) {
      bins = new Float32Array(analyser.frequencyBinCount);
      analyser.getFloatFrequencyData(bins);
      for (var i = 0; i < bins.length; i = i + 1) {
        cc_output.push(bins[i]);
      }
      //cc_output.extend(bins);
      analyser.disconnect();
      scriptProcessor.disconnect();
      gain.disconnect();
      console.log("Hello");
      results = cc_output.slice(0,30);
      console.log(results);
      _this.runCcFpFinished(results);
      //console.log("CC result:",cc_output.slice(0,30));
      //set_result(cc_output.slice(0, 30), 'cc_result');   
      //draw_fp(bins);
    };

    oscillator.start(0);
    console.log("Test");
    console.log(results);
    return results;
  }

  // Performs a hybrid of cc/pxi methods found above
  var run_hybrid_fp = function(_this) {
    var hybrid_output = [];
    var audioCtx = new(window.AudioContext || window.webkitAudioContext),
    oscillator = audioCtx.createOscillator(),
    analyser = audioCtx.createAnalyser(),
    gain = audioCtx.createGain(),
    scriptProcessor = audioCtx.createScriptProcessor(4096, 1, 1);

    // Create and configure compressor
    compressor = audioCtx.createDynamicsCompressor();
    compressor.threshold && (compressor.threshold.value = -50);
    compressor.knee && (compressor.knee.value = 40);
    compressor.ratio && (compressor.ratio.value = 12);
    compressor.reduction && (compressor.reduction.value = -20);
    compressor.attack && (compressor.attack.value = 0);
    compressor.release && (compressor.release.value = .25);

    gain.gain.value = 0; // Disable volume
    oscillator.type = "triangle"; // Set oscillator to output triangle wave
    oscillator.connect(compressor); // Connect oscillator output to dynamic compressor
    compressor.connect(analyser); // Connect compressor to analyser
    analyser.connect(scriptProcessor); // Connect analyser output to scriptProcessor input
    scriptProcessor.connect(gain); // Connect scriptProcessor output to gain input
    gain.connect(audioCtx.destination); // Connect gain output to audiocontext destination

    scriptProcessor.onaudioprocess = function (bins) {
      bins = new Float32Array(analyser.frequencyBinCount);
      analyser.getFloatFrequencyData(bins);
      for (var i = 0; i < bins.length; i = i + 1) {
        hybrid_output.push(bins[i]);
      }
      analyser.disconnect();
      scriptProcessor.disconnect();
      gain.disconnect();
      //console.log("Hybrid result:",hybrid_output.slice(0,30));
      //set_result(hybrid_output.slice(0,30), 'hybrid_result');   
      //draw_fp(bins);
      _this.runHybridFpFinished(hybrid_output.slice(0, 30));
    };

    oscillator.start(0);
    return hybrid_output.slice(0,30);
  }
  //END INSERTION OF AUDIOFINGERPRINT CODE
  this.nextID = 0;
  this.getID = function(){
    if (this.finished) {
      throw "Can't  generate ID anymore";
      return -1;
    }
    return this.nextID ++;
  }

  this.getIDs = function(numIDs) {
    var idList = [];
    for (var i = 0;i < numIDs;++ i) {
      idList.push(this.getID());
    }
    return idList;
  }

  // used for sending images back to server
  this.getData = function(gl, canvas, id) {
    var dataurl = canvas.toDataURL('image/png', 1.0);
    $.ajax({
      context:this,
      url : "http://" + ip_address + "/pictures",
      type : 'POST',
      async: false,
      data : {
        imageBase64: dataurl
      },
      success : function(img_id) {
        this.setGPUTestPostData(calcSHA1(dataurl), id, img_id);
        //parent.postMessage(data,"http://uniquemachine.org");
      },
      error: function (xhr, ajaxOptions, thrownError) {
        //alert(thrownError);
      }
    });
  }

  //this function is used to set the postdata of gpu test
  this.setGPUTestPostData = function(hashValue, id, img_id) {
    this.postData['gpuImgs'][id] = img_id + '_' + hashValue;
  }

  this.getPostData = function() {
    // get every basic features
    this.postData['timezone'] = new Date().getTimezoneOffset();
    this.postData['resolution'] = this.getResolution();
    this.postData['plugins'] = this.getPlugins();
    this.postData['cookie'] = navigator.cookieEnabled;
    this.postData['localstorage'] = this.checkLocalStorage();
    this.postData['adBlock'] = $('#ad')[0] == null ? 'Yes' : 'No';
    cvs_test = CanvasTest();
    // here we assume that the ID for canvas is 28
    // ===========================================
    // Maybe dangerous for later usage
    // ===========================================
    this.getData(null, cvs_test, 28);
    var cvs_dataurl = cvs_test.toDataURL('image/png', 1.0);

    this.postData['canvas_test'] = Base64EncodeUrlSafe(calcSHA1(cvs_dataurl.substring(22, cvs_dataurl.length))); //remove the leading words
    this.postData['cpu_cores'] = this.getCPUCores();
    this.postData['audio'] = this.audioFingerPrinting();
    this.postData['langsDetected'] = get_writing_scripts();

    // this is the WebGL information part
    this.testGL = this.getWebGL();
    if (this.testGL) this.postData['WebGL'] = true;
    else this.postData['WebGL'] = false;
    this.postData['inc'] = "Not Supported";
    this.postData['gpu'] = "Not Supported";

    if (this.postData['WebGL']) { 
      this.postData['inc'] = this.getInc(this.testGL);
      this.postData['gpu'] = this.getGpu(this.testGL);
    }

    //this part is used for WebGL rendering and flash font detection
    //these two part are async, so we need callback functions here
    this.webglFinished = function() {
      this.flashFontsDetection(this);
    }

    this.flashFontsDetectionFinished = function(fontsStr) {
      run_cc_fp(this);
    }

    this.runCcFpFinished = function(data) {
      this.postData['cc_audio'] = data.join('_');
      run_hybrid_fp(this);
    }

    this.runHybridFpFinished = function(data) {
      this.postData['hybrid_audio'] = data.join('_');
      console.log(this.postData);
      this.startSend();
    }

    webGLTest(this);

    //startSend(this.postData);
    console.log(this.postData);

    this.startSend = function(){
      $.ajax({
        url : "http://" + ip_address + "/features",
        dataType : "json",
        contentType: 'application/json',
        type : 'POST',
        data : JSON.stringify(this.postData),
        success : function(data) {
          console.log(data);
          parent.postMessage(data,"http://lab.songli.io/site/test_site/");
          //parent.postMessage(data,"http://uniquemachine.org");
        },
        error: function (xhr, ajaxOptions, thrownError) {
          alert(thrownError);
        }
      });
    }
  }
};

/* Converts the charachters that aren't UrlSafe to ones that are and
   removes the padding so the base64 string can be sent
   */
Base64EncodeUrlSafe = function(str) {
  return str.replace(/\+/g, '-').replace(/\//g, '_').replace(/\=+$/, '');
};

stringify = function(array) {
  var str = "";
  for (var i = 0, len = array.length; i < len; i += 4) {
    str += String.fromCharCode(array[i + 0]);
    str += String.fromCharCode(array[i + 1]);
    str += String.fromCharCode(array[i + 2]);
  }

  // NB: AJAX requires that base64 strings are in their URL safe
  // form and don't have any padding
  var b64 = window.btoa(str);
  return Base64EncodeUrlSafe(b64);
};

function getFingerprint() {
  var collector = new Collector();
  collector.getPostData();
}
