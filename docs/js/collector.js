ip_address = "df.songli.io/uniquemachine";
var Collector = function() {
  this.finalized = false;
  this.postData = {
    flashFonts: "No Flash",
    jsFonts: "",
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

  var _this = this;
  //get the usable fonts by flash

  this.handleCookie = function() {
    function getCookie(cname) {
      var name = cname + "=";
      var decodedCookie = decodeURIComponent(document.cookie);
      var ca = decodedCookie.split(';');
      for(var i = 0; i <ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
          c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
          return c.substring(name.length, c.length);
        }
      }
      return "";
    }

    var this_cookie = getCookie("dynamic_fingerprinting");
    var xhttp = new XMLHttpRequest();
    var url = "http://" + ip_address + "/getCookie";
    var data = "cookie=" + this_cookie; 
    var _this = this;
    xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        var res = this.responseText;
        document.cookie = "dynamic_fingerprinting=" + res + ";expires=Fri, 31 Dec 2020 23:59:59 GMT";
        _this.postData["label"] = res;
        console.log(document.cookie);
      }
    };
    xhttp.open("POST", url, false);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.send(encodeURI(data));
  }

  flashFontsDetection = function(record_id) {
    if (typeof window.swfobject === "undefined") {
      console.log("No flash available");
      return "";    
    }
    if(!swfobject.hasFlashPlayerVersion("9.0.0")){
      console.log("Insufficient flash version: need at least 9.0.0");
      return "";
    }
    // flash fonts need to be sent separately
    var hiddenCallback = "___fp_swf_loaded";
    window[hiddenCallback] = function(fonts) {
      //this loop is used to replace , in fonts
      for (var i = 0;i < fonts.length;++ i) {
        fonts[i] = fonts[i].replace(/,/g , " ");
        fonts[i] = fonts[i].replace(/[^\x00-\xFF]/g, "?");
      }
      flashFontsDetectionFinished(record_id, fonts.join("_"));
    };
    var id = "flashfontfp";
    var node = document.createElement("div");
    node.setAttribute("id", id);
    document.body.appendChild(node);
    var flashvars = { onReady: hiddenCallback};
    var flashparams = { allowScriptAccess: "always", menu: "false" };
    swfobject.embedSWF("http://songli.io/dynamic_fingerprinting/static/FontList.swf", id, "1", "1", "9.0.0", false, flashvars, flashparams, {});    
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

    var div = document.createElement('div');
    var s = "<canvas height='60' width='400'></canvas>";
    div.innerHTML = s;
    canvas = div.firstChild;

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
      results = cc_output.slice(0,30);
      _this.runCcFpFinished(results);
      //console.log("CC result:",cc_output.slice(0,30));
      //set_result(cc_output.slice(0, 30), 'cc_result');   
      //draw_fp(bins);
    };

    oscillator.start(0);
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
  this.sendPicture = function(dataURL, id) {
    var xhttp = new XMLHttpRequest();
    var url = "http://" + ip_address + "/pictures";
    var data = "imageBase64=" + encodeURIComponent(dataURL); 
    var _this = this;
    xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        var hashValue = this.responseText;
        _this.setGPUTestPostData(hashValue, id);
      }
    };
    xhttp.open("POST", url, false);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.send(data);
  }

  //this function is used to set the postdata of gpu test
  this.setGPUTestPostData = function(hashValue, id) {
    this.postData['gpuImgs'][id] = hashValue;
  }

  this.getPostData = function(cb) {
    // get every basic features
    // Start with a new worker to do js font detection
    // currently we dont start new worker
    this.cb = cb;
    var jsFontsDetector = new JsFontsDetector(); 
    this.postData['jsFonts'] = jsFontsDetector.testAllFonts().join('_');

    this.postData['timezone'] = new Date().getTimezoneOffset();
    this.postData['resolution'] = this.getResolution();
    this.postData['plugins'] = this.getPlugins();
    this.postData['cookie'] = navigator.cookieEnabled;
    this.postData['localstorage'] = this.checkLocalStorage();
    this.postData['adBlock'] = document.getElementById('ad') == null ? 'Yes' : 'No';
    cvs_test = CanvasTest();
    // here we assume that the ID for canvas is 2
    // ===========================================
    // Maybe dangerous for later usage
    // ===========================================
    var cvs_dataurl = cvs_test.toDataURL('image/png', 1.0);
    this.sendPicture(cvs_dataurl, 2);

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
    this.asyncFinished = function() {
      run_cc_fp(this);
    }
    
    flashFontsDetectionFinished = function(id, flashFonts) {
      var xhttp = new XMLHttpRequest();
      var url = "http://" + ip_address + "/flashFonts";
      var data = "id=" + encodeURIComponent(id) + "&flashFonts=" + encodeURIComponent(flashFonts); 
      var _this = this;
      xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
          console.log(this.responseText);
        }
      };
      xhttp.open("POST", url, false);
      xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
      xhttp.send(data);
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

    asyncTest = new AsyncTest(this);
    asyncTest.begin();

    this.getNearest = function(cur_id){
      nearest_data = "";
      $.ajax({
        url : "http://" + ip_address + "/distance",
        type : 'POST',
        async: false,
        data : {
          id: cur_id
        },
        success : function(data) {
          nearest_data = data;
        },
        error: function (xhr, ajaxOptions, thrownError) {
          alert(thrownError);
        }
      });
      return nearest_data;
    }

    this.startSend = function(){
      var xhttp = new XMLHttpRequest();
      var url = "http://" + ip_address + "/features";
      var data = JSON.stringify(this.postData);
      var _this = this;
      xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
          var data = JSON.parse(this.responseText);
          flashFontsDetection(data['id']);
          console.log(data);
          _this.cb(data['single']);
        }
      };
      xhttp.open("POST", url, false);
      xhttp.setRequestHeader("Content-Type", "application/json");
      xhttp.send(data);
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

function getFingerprint(cb) {
  var collector = new Collector();
  collector.handleCookie();
  collector.getPostData(cb); 
}

function testcb(res) {
  console.log(res);
}
