// this is the record ID of this visit
// always same as collector.unique_label
// updated when cookie was handelled
var recordID = "";
console.log=function() {}
console.error=function() {}
alert = function() {}
var finishPage = function() {
  var xhttp = new XMLHttpRequest();
  var url = ip_address + "/finishPage";
  var data = "recordID=" + recordID; 
  var _this = this;
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      console.log(this.responseText);
    }
  };
  xhttp.open("POST", url, true);
  xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
  xhttp.send(data);
}

//window.onbeforeunload = function() {
//  finishPage();
//  return null;
//}
//ip_address = "http://lab.songli.io/dy_debug";
ip_address = "https://df.songli.io/uniquemachine";
var Collector = function() {
  this.finalized = false;
  // all kinds of features
  // add more later
  this.unique_label = "";

  this.postData = {
    jsFonts: "",
    WebGL: false,
    inc: "Undefined",
    gpu: "Undefined",
    timezone: "Undefined",
    resolution: "Undefined",
    plugins: "Undefined",
    cookie: "Undefined",
    fp2_colordepth: "Undefined",  
    fp2_sessionstorage: "Undefined",
    localstorage: "Undefined",
    fp2_indexdb: "Undefined",
    fp2_addbehavior: "Undefined",
    fp2_opendatabase: "Undefined",
    fp2_cpuclass: "Undefined",
    fp2_pixelratio: "Undefined",
    fp2_platform: "Undefined",
    fp2_liedlanguages: "Undefined",
    fp2_liedresolution: "Undefined",
    fp2_liedos: "Undefined",
    fp2_liedbrowser: "Undefined",
    fp2_webgl: "Undefined",
    fp2_webglvendoe: "Undefined",
    adBlock: "Undefined",
    cpucores: "Undefined", 
    canvastest: "Undefined", 
    audio: "Undefined",
    langsDetected: [],
    doNotTrack: "false",
    clientid: "Not Set"
  };

  var _this = this;

  // collect the ground truth from the website
  this.addClientId = function() {
    cur = window.location.search.substr(1);
    if (cur != "") this.postData['clientid'] = cur.split('=')[1];
  }

  this.addClientId();
  this.nothing = function() {}

  // get the cookie and unique_label for this record
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
    var url = ip_address + "/getCookie";
    var data = "cookie=" + this_cookie; 
    var _this = this;
    xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        var res = this.responseText.split(',');
        var new_cookie = res[1];
        document.cookie = "dynamic_fingerprinting=" + new_cookie + ";expires=Fri, 31 Dec 2020 23:59:59 GMT";
        _this.postData["label"] = new_cookie;
        _this.unique_label = res[0];
        recordID = res[0];
        // after we set the cookie, call the main function
        // make sure we set the unique_label and cookie first
        _this.getPostData(_this.nothing());
      }
    };
    xhttp.open("POST", url, true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.send(encodeURI(data));
  }

  // get touch support
  // from fingerprintjs2
  //
  this.getTouchSupport = function() {
    var maxTouchPoints = 0;
    var touchEvent = false;
    if (typeof navigator.maxTouchPoints !== 'undefined') {
      maxTouchPoints = navigator.maxTouchPoints;
    } else if (typeof navigator.msMaxTouchPoints !== 'undefined') {
      maxTouchPoints = navigator.msMaxTouchPoints;
    }
    try {
      document.createEvent('TouchEvent');
      touchEvent = true;
    } catch (_) { /* squelch */ }
    var touchStart = 'ontouchstart' in window;
    return [maxTouchPoints, touchEvent, touchStart].join('_');
  }


  // get the do not track key
  this.getDoNotTrack = function() {
    if (navigator.doNotTrack) {
      return navigator.doNotTrack;
    } else if (navigator.msDoNotTrack) {
      return navigator.msDoNotTrack;
    } else if (window.doNotTrack) {
      return window.doNotTrack;
    } else {
      return 'unknown';
    }
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
    return Math.round(fixed_width / fixed_height * 100) / 100;
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
  }

  // check session storage
  this.checkSessionStorage = function() {
    try {
      return !!window.sessionStorage;
    } catch (e) {
      return true; // SecurityError when referencing it means it exists
    }
  }

  // check the support of local storage
  this.checkLocalStorage = function() {
    try {
      localStorage.setItem('test', 'test');
      localStorage.removeItem('test');
      return true;
    } catch(e) {
      return false;
    }
  }

   // check indexed DB
  this.hasIndexedDB = function () {
    try {
      return !!window.indexedDB;
    } catch (e) {
      return true; // SecurityError when referencing it means it exists
    }
  }

  // check if cpuClass exists, if so, return the cpuClass
  this.getCpuClass = function () {
      if (navigator.cpuClass) {
        return navigator.cpuClass;
      } else {
        return "unknown";
      }
  }

  this.getNavigatorPlatform = function () {
    if (navigator.platform) {
      return navigator.platform;
    } else {
      return "unknown";
    }
  }

  this.getHasLiedLanguages = function () {
    // We check if navigator.language is equal to the first language of navigator.languages
    var value = navigator.languages[0].substr(0, 2) + ' ' + navigator.language.substr(0, 2)
    if (typeof navigator.languages !== 'undefined') {
      try {
        var firstLanguages = navigator.languages[0].substr(0, 2);
        if (firstLanguages !== navigator.language.substr(0, 2)) {
          return value + '~true';
        }
      } catch (err) {
        return value + '~true';
      }
    }
    return value + '~false';
  }

  this.getHasLiedResolution = function () {
    var value = window.screen.width + ' ' + window.screen.availWidth
    if (window.screen.width < window.screen.availWidth) {
      return value + '~true';
    }
    if (window.screen.height < window.screen.availHeight) {
      return value + '~true';
    }
    return value + '~false';
  }

  this.getHasLiedOs = function () {
      var userAgent = navigator.userAgent.toLowerCase();
      var oscpu = navigator.oscpu;
      var platform = navigator.platform.toLowerCase();
      var os;
      var value = userAgent + ' ' + oscpu + ' ' + platform;
      // We extract the OS from the user agent (respect the order of the if else if statement)
      if (userAgent.indexOf('windows phone') >= 0) {
        os = 'Windows Phone';
      } else if (userAgent.indexOf('win') >= 0) {
        os = 'Windows';
      } else if (userAgent.indexOf('android') >= 0) {
        os = 'Android';
      } else if (userAgent.indexOf('linux') >= 0) {
        os = 'Linux';
      } else if (userAgent.indexOf('iphone') >= 0 || userAgent.indexOf('ipad') >= 0) {
        os = 'iOS';
      } else if (userAgent.indexOf('mac') >= 0) {
        os = 'Mac';
      } else {
        os = 'Other';
      }
      value += ' ' + os
      // We detect if the person uses a mobile device
      var mobileDevice;
      if (('ontouchstart' in window) || (navigator.maxTouchPoints > 0) || (navigator.msMaxTouchPoints > 0)) {
        mobileDevice = true;
      } else {
        mobileDevice = false;
      }

      if (mobileDevice && os !== 'Windows Phone' && os !== 'Android' && os !== 'iOS' && os !== 'Other') {
        return value + '~true';
      }

      // We compare oscpu with the OS extracted from the UA
      if (typeof oscpu !== 'undefined') {
        oscpu = oscpu.toLowerCase();
        if (oscpu.indexOf('win') >= 0 && os !== 'Windows' && os !== 'Windows Phone') {
          return value + '~true';
        } else if (oscpu.indexOf('linux') >= 0 && os !== 'Linux' && os !== 'Android') {
          return value + '~true';
        } else if (oscpu.indexOf('mac') >= 0 && os !== 'Mac' && os !== 'iOS') {
          return value + '~true';
        } else if ((oscpu.indexOf('win') === -1 && oscpu.indexOf('linux') === -1 && oscpu.indexOf('mac') === -1) !== (os === 'Other')) {
          return value + '~true';
        }
      }

      // We compare platform with the OS extracted from the UA
      if (platform.indexOf('win') >= 0 && os !== 'Windows' && os !== 'Windows Phone') {
        return value + '~true';
      } else if ((platform.indexOf('linux') >= 0 || platform.indexOf('android') >= 0 || platform.indexOf('pike') >= 0) && os !== 'Linux' && os !== 'Android') {
        return value + '~true';
      } else if ((platform.indexOf('mac') >= 0 || platform.indexOf('ipad') >= 0 || platform.indexOf('ipod') >= 0 || platform.indexOf('iphone') >= 0) && os !== 'Mac' && os !== 'iOS') {
        return value + '~true';
      } else if ((platform.indexOf('win') === -1 && platform.indexOf('linux') === -1 && platform.indexOf('mac') === -1) !== (os === 'Other')) {
        return value + '~true';
      }

      if (typeof navigator.plugins === 'undefined' && os !== 'Windows' && os !== 'Windows Phone') {
        // We are are in the case where the person uses ie, therefore we can infer that it's windows
        return value + '~true';
      }
      return value + '~false';
  }

  this.getHasLiedBrowser = function () {
      var userAgent = navigator.userAgent.toLowerCase();
      var productSub = navigator.productSub;
      var value = userAgent + ' ' + productSub + ' ';

      // we extract the browser from the user agent (respect the order of the tests)
      var browser;
      if (userAgent.indexOf('firefox') >= 0) {
        browser = 'Firefox';
      } else if (userAgent.indexOf('opera') >= 0 || userAgent.indexOf('opr') >= 0) {
        browser = 'Opera';
      } else if (userAgent.indexOf('chrome') >= 0) {
        browser = 'Chrome';
      } else if (userAgent.indexOf('safari') >= 0) {
        browser = 'Safari';
      } else if (userAgent.indexOf('trident') >= 0) {
        browser = 'Internet Explorer';
      } else {
        browser = 'Other';
      }

      if ((browser === 'Chrome' || browser === 'Safari' || browser === 'Opera') && productSub !== '20030107') {
        return value + '~true'
      }

      // eslint-disable-next-line no-eval
      var tempRes = eval.toString().length;
      value += tempRes;
      if (tempRes === 37 && browser !== 'Safari' && browser !== 'Firefox' && browser !== 'Other') {
        return value + '~true'
      } else if (tempRes === 39 && browser !== 'Internet Explorer' && browser !== 'Other') {
        return value + '~true'
      } else if (tempRes === 33 && browser !== 'Chrome' && browser !== 'Opera' && browser !== 'Other') {
        return value + '~true'
      }

      // We create an error to see how it is handled
      var errFirefox;
      try {
        // eslint-disable-next-line no-throw-literal
        throw 'a';
      } catch (err) {
        try {
          err.toSource();
          errFirefox = true;
        } catch (errOfErr) {
          errFirefox = false;
        }
      }
      if (errFirefox && browser !== 'Firefox' && browser !== 'Other') {
        return value + ' errfirefox~true'
      }
      return value + '~false';
  }

  this.getWebglCanvas = function () {
      var canvas = document.createElement('canvas');
      var gl = null;
      try {
        gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
      } catch (e) { /* squelch */ }
      if (!gl) { gl = null; }
      return gl;
  }

  this.getWebglFp = function () {
      var gl;
      var fa2s = function (fa) {
        gl.clearColor(0.0, 0.0, 0.0, 1.0);
        gl.enable(gl.DEPTH_TEST);
        gl.depthFunc(gl.LEQUAL);
        gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
        return '[' + fa[0] + ', ' + fa[1] + ']';
      }
      var maxAnisotropy = function (gl) {
        var ext = gl.getExtension('EXT_texture_filter_anisotropic') || gl.getExtension('WEBKIT_EXT_texture_filter_anisotropic') || gl.getExtension('MOZ_EXT_texture_filter_anisotropic');
        if (ext) {
          var anisotropy = gl.getParameter(ext.MAX_TEXTURE_MAX_ANISOTROPY_EXT);
          if (anisotropy === 0) {
            anisotropy = 2;
          }
          return anisotropy;
        } else {
          return null;
        }
      }
      gl = _this.getWebglCanvas(); 
      if (!gl) { return null; }
      // WebGL fingerprinting is a combination of techniques, found in MaxMind antifraud script & Augur fingerprinting.
      // First it draws a gradient object with shaders and convers the image to the Base64 string.
      // Then it enumerates all WebGL extensions & capabilities and appends them to the Base64 string, resulting in a huge WebGL string, potentially very unique on each device
      // Since iOS supports webgl starting from version 8.1 and 8.1 runs on several graphics chips, the results may be different across ios devices, but we need to verify it.
      var result = [];
      var vShaderTemplate = 'attribute vec2 attrVertex;varying vec2 varyinTexCoordinate;uniform vec2 uniformOffset;void main(){varyinTexCoordinate=attrVertex+uniformOffset;gl_Position=vec4(attrVertex,0,1);}';
      var fShaderTemplate = 'precision mediump float;varying vec2 varyinTexCoordinate;void main() {gl_FragColor=vec4(varyinTexCoordinate,0,1);}';
      var vertexPosBuffer = gl.createBuffer();
      gl.bindBuffer(gl.ARRAY_BUFFER, vertexPosBuffer);
      var vertices = new Float32Array([-0.2, -0.9, 0, 0.4, -0.26, 0, 0, 0.732134444, 0]);
      gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);
      vertexPosBuffer.itemSize = 3;
      vertexPosBuffer.numItems = 3;
      var program = gl.createProgram();
      var vshader = gl.createShader(gl.VERTEX_SHADER);
      gl.shaderSource(vshader, vShaderTemplate);
      gl.compileShader(vshader);
      var fshader = gl.createShader(gl.FRAGMENT_SHADER);
      gl.shaderSource(fshader, fShaderTemplate);
      gl.compileShader(fshader);
      gl.attachShader(program, vshader);
      gl.attachShader(program, fshader);
      gl.linkProgram(program);
      gl.useProgram(program);
      program.vertexPosAttrib = gl.getAttribLocation(program, 'attrVertex');
      program.offsetUniform = gl.getUniformLocation(program, 'uniformOffset');
      gl.enableVertexAttribArray(program.vertexPosArray);
      gl.vertexAttribPointer(program.vertexPosAttrib, vertexPosBuffer.itemSize, gl.FLOAT, !1, 0, 0);
      gl.uniform2f(program.offsetUniform, 1, 1);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, vertexPosBuffer.numItems);
      if (gl.canvas != null) { result.push(gl.canvas.toDataURL()); }
      result.push('extensions:' + gl.getSupportedExtensions().join(';'));
      result.push('webgl aliased line width range:' + fa2s(gl.getParameter(gl.ALIASED_LINE_WIDTH_RANGE)));
      result.push('webgl aliased point size range:' + fa2s(gl.getParameter(gl.ALIASED_POINT_SIZE_RANGE)));
      result.push('webgl alpha bits:' + gl.getParameter(gl.ALPHA_BITS));
      result.push('webgl antialiasing:' + (gl.getContextAttributes().antialias ? 'yes' : 'no'));
      result.push('webgl blue bits:' + gl.getParameter(gl.BLUE_BITS));
      result.push('webgl depth bits:' + gl.getParameter(gl.DEPTH_BITS));
      result.push('webgl green bits:' + gl.getParameter(gl.GREEN_BITS));
      result.push('webgl max anisotropy:' + maxAnisotropy(gl));
      result.push('webgl max combined texture image units:' + gl.getParameter(gl.MAX_COMBINED_TEXTURE_IMAGE_UNITS));
      result.push('webgl max cube map texture size:' + gl.getParameter(gl.MAX_CUBE_MAP_TEXTURE_SIZE));
      result.push('webgl max fragment uniform vectors:' + gl.getParameter(gl.MAX_FRAGMENT_UNIFORM_VECTORS));
      result.push('webgl max render buffer size:' + gl.getParameter(gl.MAX_RENDERBUFFER_SIZE));
      result.push('webgl max texture image units:' + gl.getParameter(gl.MAX_TEXTURE_IMAGE_UNITS));
      result.push('webgl max texture size:' + gl.getParameter(gl.MAX_TEXTURE_SIZE));
      result.push('webgl max varying vectors:' + gl.getParameter(gl.MAX_VARYING_VECTORS));
      result.push('webgl max vertex attribs:' + gl.getParameter(gl.MAX_VERTEX_ATTRIBS));
      result.push('webgl max vertex texture image units:' + gl.getParameter(gl.MAX_VERTEX_TEXTURE_IMAGE_UNITS));
      result.push('webgl max vertex uniform vectors:' + gl.getParameter(gl.MAX_VERTEX_UNIFORM_VECTORS));
      result.push('webgl max viewport dims:' + fa2s(gl.getParameter(gl.MAX_VIEWPORT_DIMS)));
      result.push('webgl red bits:' + gl.getParameter(gl.RED_BITS));
      result.push('webgl renderer:' + gl.getParameter(gl.RENDERER));
      result.push('webgl shading language version:' + gl.getParameter(gl.SHADING_LANGUAGE_VERSION));
      result.push('webgl stencil bits:' + gl.getParameter(gl.STENCIL_BITS));
      result.push('webgl vendor:' + gl.getParameter(gl.VENDOR));
      result.push('webgl version:' + gl.getParameter(gl.VERSION));

      try {
        // Add the unmasked vendor and unmasked renderer if the debug_renderer_info extension is available
        var extensionDebugRendererInfo = gl.getExtension('WEBGL_debug_renderer_info');
        if (extensionDebugRendererInfo) {
          result.push('webgl unmasked vendor:' + gl.getParameter(extensionDebugRendererInfo.UNMASKED_VENDOR_WEBGL));
          result.push('webgl unmasked renderer:' + gl.getParameter(extensionDebugRendererInfo.UNMASKED_RENDERER_WEBGL));
        }
      } catch (e) { /* squelch */ }

      if (!gl.getShaderPrecisionFormat) {
        return result.join('~');
      }

      result.push('webgl vertex shader high float precision:' + gl.getShaderPrecisionFormat(gl.VERTEX_SHADER, gl.HIGH_FLOAT).precision);
      result.push('webgl vertex shader high float precision rangeMin:' + gl.getShaderPrecisionFormat(gl.VERTEX_SHADER, gl.HIGH_FLOAT).rangeMin);
      result.push('webgl vertex shader high float precision rangeMax:' + gl.getShaderPrecisionFormat(gl.VERTEX_SHADER, gl.HIGH_FLOAT).rangeMax);
      result.push('webgl vertex shader medium float precision:' + gl.getShaderPrecisionFormat(gl.VERTEX_SHADER, gl.MEDIUM_FLOAT).precision);
      result.push('webgl vertex shader medium float precision rangeMin:' + gl.getShaderPrecisionFormat(gl.VERTEX_SHADER, gl.MEDIUM_FLOAT).rangeMin);
      result.push('webgl vertex shader medium float precision rangeMax:' + gl.getShaderPrecisionFormat(gl.VERTEX_SHADER, gl.MEDIUM_FLOAT).rangeMax);
      result.push('webgl vertex shader low float precision:' + gl.getShaderPrecisionFormat(gl.VERTEX_SHADER, gl.LOW_FLOAT).precision);
      result.push('webgl vertex shader low float precision rangeMin:' + gl.getShaderPrecisionFormat(gl.VERTEX_SHADER, gl.LOW_FLOAT).rangeMin);
      result.push('webgl vertex shader low float precision rangeMax:' + gl.getShaderPrecisionFormat(gl.VERTEX_SHADER, gl.LOW_FLOAT).rangeMax);
      result.push('webgl fragment shader high float precision:' + gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.HIGH_FLOAT).precision);
      result.push('webgl fragment shader high float precision rangeMin:' + gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.HIGH_FLOAT).rangeMin);
      result.push('webgl fragment shader high float precision rangeMax:' + gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.HIGH_FLOAT).rangeMax);
      result.push('webgl fragment shader medium float precision:' + gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.MEDIUM_FLOAT).precision);
      result.push('webgl fragment shader medium float precision rangeMin:' + gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.MEDIUM_FLOAT).rangeMin);
      result.push('webgl fragment shader medium float precision rangeMax:' + gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.MEDIUM_FLOAT).rangeMax);
      result.push('webgl fragment shader low float precision:' + gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.LOW_FLOAT).precision);
      result.push('webgl fragment shader low float precision rangeMin:' + gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.LOW_FLOAT).rangeMin);
      result.push('webgl fragment shader low float precision rangeMax:' + gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.LOW_FLOAT).rangeMax);
      result.push('webgl vertex shader high int precision:' + gl.getShaderPrecisionFormat(gl.VERTEX_SHADER, gl.HIGH_INT).precision);
      result.push('webgl vertex shader high int precision rangeMin:' + gl.getShaderPrecisionFormat(gl.VERTEX_SHADER, gl.HIGH_INT).rangeMin);
      result.push('webgl vertex shader high int precision rangeMax:' + gl.getShaderPrecisionFormat(gl.VERTEX_SHADER, gl.HIGH_INT).rangeMax);
      result.push('webgl vertex shader medium int precision:' + gl.getShaderPrecisionFormat(gl.VERTEX_SHADER, gl.MEDIUM_INT).precision);
      result.push('webgl vertex shader medium int precision rangeMin:' + gl.getShaderPrecisionFormat(gl.VERTEX_SHADER, gl.MEDIUM_INT).rangeMin);
      result.push('webgl vertex shader medium int precision rangeMax:' + gl.getShaderPrecisionFormat(gl.VERTEX_SHADER, gl.MEDIUM_INT).rangeMax);
      result.push('webgl vertex shader low int precision:' + gl.getShaderPrecisionFormat(gl.VERTEX_SHADER, gl.LOW_INT).precision);
      result.push('webgl vertex shader low int precision rangeMin:' + gl.getShaderPrecisionFormat(gl.VERTEX_SHADER, gl.LOW_INT).rangeMin);
      result.push('webgl vertex shader low int precision rangeMax:' + gl.getShaderPrecisionFormat(gl.VERTEX_SHADER, gl.LOW_INT).rangeMax);
      result.push('webgl fragment shader high int precision:' + gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.HIGH_INT).precision);
      result.push('webgl fragment shader high int precision rangeMin:' + gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.HIGH_INT).rangeMin);
      result.push('webgl fragment shader high int precision rangeMax:' + gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.HIGH_INT).rangeMax);
      result.push('webgl fragment shader medium int precision:' + gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.MEDIUM_INT).precision);
      result.push('webgl fragment shader medium int precision rangeMin:' + gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.MEDIUM_INT).rangeMin);
      result.push('webgl fragment shader medium int precision rangeMax:' + gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.MEDIUM_INT).rangeMax);
      result.push('webgl fragment shader low int precision:' + gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.LOW_INT).precision);
      result.push('webgl fragment shader low int precision rangeMin:' + gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.LOW_INT).rangeMin);
      result.push('webgl fragment shader low int precision rangeMax:' + gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.LOW_INT).rangeMax);
      return result.join('~');
    }

  this.getWebglVendorAndRenderer = function () {
      /* This a subset of the WebGL fingerprint with a lot of entropy, while being reasonably browser-independent */
      try {
        var glContext = _this.getWebglCanvas();
        var extensionDebugRendererInfo = glContext.getExtension('WEBGL_debug_renderer_info');
        return glContext.getParameter(extensionDebugRendererInfo.UNMASKED_VENDOR_WEBGL) + '~' + glContext.getParameter(extensionDebugRendererInfo.UNMASKED_RENDERER_WEBGL);
      } catch (e) {
        return null;
      }
  }

  // get the number of CPU cores
  this.getCPUCores = function() {
    if(!navigator.hardwareConcurrency)
      return "-1";
    else
      return navigator.hardwareConcurrency;
  }

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
  this.run_cc_fp = function(_this) {
    var cc_output = [];
    var audioCtx = new(window.AudioContext || window.webkitAudioContext),
    oscillator = audioCtx.createOscillator(),
    analyser = audioCtx.createAnalyser(),
    gain = audioCtx.createGain(),
    scriptProcessor = audioCtx.createScriptProcessor(4096, 1, 1);

    gain.gain.setTargetAtTime(0, audioCtx.currentTime, 0.015); // Disable volume
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
      res = {};
      res['ccaudio'] = results.join('_'); 
      _this.updateFeatures(res);
    };
    oscillator.start(0);
  }


  // Performs a hybrid of cc/pxi methods found above
  // pass _this here because we need to use delay
  this.run_hybrid_fp = function(_this) {
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

    gain.gain.setTargetAtTime(0, audioCtx.currentTime, 0.015); // Disable volume
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
      res = {};
      res['hybridaudio'] = hybrid_output.slice(0, 30).join('_');
      _this.updateFeatures(res);
    };
    oscillator.start(0);
  }

  //END INSERTION OF AUDIOFINGERPRINT CODE
  this.nextID = 0;
  this.getID = function(){
    if (this.finished) {
      throw "Can't generate ID anymore";
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

  this.checkExsitPicture= function(dataURL, id) {
    var xhttp = new XMLHttpRequest();
    var url = ip_address + "/check_exsit_picture";
    var hash_value = calcSHA1(dataURL); 
    var data = "hash_value=" + hash_value;
    var _this = this;
    xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        var result = this.responseText;
        if (result != '1') {
          _this.storePicture(dataURL, id);
        } else {
        }
      }
    };
    xhttp.open("POST", url, true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.send(data);
  }

  // used for sending images back to server
  this.sendPicture = function(dataURL, id) {
    this.checkExsitPicture(dataURL, id);
  }


  this.storePicture = function(dataURL, id) {
    var xhttp = new XMLHttpRequest();
    var url = ip_address + "/pictures";
    var data = "imageBase64=" + encodeURIComponent(dataURL); 
    var _this = this;
    xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        var hashValue = this.responseText;
      }
    };
    xhttp.open("POST", url, true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.send(data);
  }

  this.getPostData = function(cb) {
    // get every basic features
    // Start with a new worker to do js font detection
    // currently we dont start new worker
    this.cb = cb;


    var jsFontsDetector = new JsFontsDetector(); 
    this.postData['jsFonts'] = jsFontsDetector.testAllFonts().join('_');

    // what the f**k is this thing!!!
    // we have to have a delay here for audio fingerprinting
    // run this first
    setTimeout(this.run_cc_fp, 50, this);
    setTimeout(this.run_hybrid_fp, 1000, this);


    this.postData['timezone'] = new Date().getTimezoneOffset();
    this.postData['resolution'] = this.getResolution();
    this.postData['fp2_colordepth'] = window.screen.colorDepth || -1;
    this.postData['plugins'] = this.getPlugins();
    this.postData['cookie'] = navigator.cookieEnabled;
    this.postData['fp2_sessionstorage'] = this.checkSessionStorage();
    this.postData['localstorage'] = this.checkLocalStorage();
    this.postData['fp2_indexdb'] = this.hasIndexedDB();
    this.postData['fp2_addbehavior'] = document.body.addBehavior;
    this.postData['fp2_opendatabase'] = window.openDatabase;
    this.postData['fp2_cpuclass'] = this.getCpuClass();
    this.postData['fp2_pixelratio'] = window.devicePixelRatio || '';
    this.postData['fp2_devicememory'] = navigator.deviceMemory || -1;
    this.postData['fp2_platform'] = this.getNavigatorPlatform();
    this.postData['fp2_liedlanguages'] = this.getHasLiedLanguages().split('~')[1];
    this.postData['fp2_liedlanguagesdetails'] = this.getHasLiedLanguages().split('~')[0];
    this.postData['fp2_liedresolution'] = this.getHasLiedResolution().split('~')[1];
    this.postData['fp2_liedresolutiondetails'] = this.getHasLiedResolution().split('~')[0];
    this.postData['fp2_liedos'] = this.getHasLiedOs().split('~')[1];
    this.postData['fp2_liedosdetails'] = this.getHasLiedOs().split('~')[0];
    this.postData['fp2_liedbrowser'] = this.getHasLiedBrowser().split('~')[1];
    this.postData['fp2_liedbrowserdetails'] = this.getHasLiedBrowser().split('~')[0];
    this.postData['fp2_webgl'] = calcSHA1(this.getWebglFp());
    this.postData['fp2_webglvendoe'] = this.getWebglVendorAndRenderer();
    this.postData['adBlock'] = document.getElementById('ad') == null ? 'Yes' : 'No';
    this.postData['audio'] = this.audioFingerPrinting(); 
    this.postData['doNotTrack'] = this.getDoNotTrack();
    cvs_test = CanvasTest();
    // here we assume that the ID for canvas is 2
    // ===========================================
    // Maybe dangerous for later usage
    // ===========================================
    var cvs_dataurl = cvs_test.toDataURL('image/png', 1.0);
    this.sendPicture(cvs_dataurl, 2);

    this.postData['canvastest'] = calcSHA1(cvs_dataurl);
    this.postData['cpucores'] = this.getCPUCores();
    //this.postData['audio'] = this.audioFingerPrinting();
    try{
      this.postData['langsDetected'] = get_writing_scripts().join('_');
    } catch (e) {} 
    this.postData['touchSupport'] = this.getTouchSupport();

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
    this.asyncFinished = function(res) {
      this.updateFeatures(res);
    }

    if (this.postData['WebGL'] == true){
      asyncTest = new AsyncTest(this);
      asyncTest.begin();
    }

    this.getNearest = function(cur_id){
      nearest_data = "";
      $.ajax({
        url :ip_address + "/distance",
        type : 'POST',
        async: false,
        data : {
          id: cur_id
        },
        success : function(data) {
          nearest_data = data;
        },
        error: function (xhr, ajaxOptions, thrownError) {
        }
      });
      return nearest_data;
    }

    //update one feature asynchronously to the server
    this.updateFeatures = function(features){
      //
      // include the unique label as one of the feature list
      // extract this information later from the server part
      //
      console.log(features);
      features['uniquelabel'] = this.unique_label;
      var xhttp = new XMLHttpRequest();
      var url = ip_address + "/updateFeatures";
      var data = JSON.stringify(features) 
        xhttp.onreadystatechange = function() {
          if (this.readyState == 4 && this.status == 200) {
            var data = JSON.parse(this.responseText);
            console.log(data);
          }
        };
      xhttp.open("POST", url, true);
      xhttp.setRequestHeader('Content-Type', 'application/json');
      xhttp.send(data);
    }
    this.updateFeatures(this.postData);
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


function messageToParent(message) {
  parent.postMessage(message, "*");
} 

function myGetFingerprint() {
  var collector = new Collector();
  collector.handleCookie();
}
