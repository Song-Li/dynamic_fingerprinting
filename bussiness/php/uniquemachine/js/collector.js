// this is the record ID of this visit
// always same as collector.unique_label
// updated when cookie was handelled
var recordID = "";
//console.log=function() {}
alert = function () {
}

//window.onbeforeunload = function() {
//  finishPage();
//  return null;
//}
ip_address = "http://34.250.181.209/php";
//ip_address = "http://lab.songli.io/uniquemachine";
var Collector = function () {
    this.finalized = false;
    // all kinds of features
    // add more later
    this.unique_label = "";

    this.features = {
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
    this.addClientId = function () {
        cur = window.location.search.substr(1);
        if (cur != "") return cur.split('=')[1];
        return "Not Set";
    }


    // get touch support
    // from fingerprintjs2
    //
    this.getTouchSupport = function () {
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
        } catch (_) { /* squelch */
        }
        var touchStart = 'ontouchstart' in window;
        return [maxTouchPoints, touchEvent, touchStart].join('_');
    }


    // get the do not track key

    this.getDoNotTrack = function () {
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
    this.audioFingerPrinting = function () {
        var finished = false;
        try {
            var audioCtx = new (window.AudioContext || window.webkitAudioContext),
                oscillator = audioCtx.createOscillator(),
                analyser = audioCtx.createAnalyser(),
                gainNode = audioCtx.createGain(),
                scriptProcessor = audioCtx.createScriptProcessor(4096, 1, 1);
            var destination = audioCtx.destination;
            return (audioCtx.sampleRate).toString() + '_' + destination.maxChannelCount + "_" + destination.numberOfInputs + '_' + destination.numberOfOutputs + '_' + destination.channelCount + '_' + destination.channelCountMode + '_' + destination.channelInterpretation;
        }
        catch (e) {
            return "not supported";
        }
    }


    // get the screen resolution
    this.getResolution = function () {
        var zoom_level = detectZoom.device();
        var fixed_width = window.screen.width * zoom_level;
        var fixed_height = window.screen.height * zoom_level;
        return Math.round(fixed_width / fixed_height * 100) / 100;
        var res = Math.round(fixed_width) + '_' + Math.round(fixed_height) + '_' + zoom_level + '_' + window.screen.width + "_" + window.screen.height + "_" + window.screen.colorDepth + "_" + window.screen.availWidth + "_" + window.screen.availHeight + "_" + window.screen.left + '_' + window.screen.top + '_' + window.screen.availLeft + "_" + window.screen.availTop + "_" + window.innerWidth + "_" + window.outerWidth + "_" + detectZoom.zoom();
        return res;
    }


    // get the list of plugins
    this.getPlugins = function () {
        var plgs_len = navigator.plugins.length;
        var plugins = [];
        for (var i = 0; i < plgs_len; i++) {
            plugins.push(navigator.plugins[i].name);
        }
        plugins.sort();
        var plgs = plugins.join("~");
        plgs = plgs.replace(/[^a-zA-Z~ ]/g, "");
        return plgs;
    };

    // check the support of local storage
    this.checkLocalStorage = function () {
        try {
            localStorage.setItem('test', 'test');
            localStorage.removeItem('test');
            return true;
        } catch (e) {
            return false;
        }
    };

    // get the number of CPU cores
    this.getCPUCores = function () {
        if (!navigator.hardwareConcurrency)
            return "-1"
        else
            return navigator.hardwareConcurrency;
    };

    // check the support of WebGL
    this.getWebGL = function () {
        canvas = getCanvas('tmp_canvas');
        var gl = getGL(canvas);
        return gl;
    }

    // get the inc info
    this.getInc = function (gl) {
        var debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
        if (debugInfo) return gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
        return "No Debug Info";
    }

    // get the GPU info
    this.getGpu = function (gl) {
        var debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
        if (debugInfo) return gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
        return "No Debug Info";
    }

    // get the canvas uniquemachine information

    var CanvasTest = function () {
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

    this.syncTest = function (cb, cookie) {

        this.features["clientid"] = this.addClientId();

        // this is the WebGL information part
        this.testGL = this.getWebGL();
        if (this.testGL) this.features['WebGL'] = true;
        else this.features['WebGL'] = false;
        this.features['inc'] = "Not Supported";
        this.features['gpu'] = "Not Supported";

        if (this.features['WebGL']) {
            this.features['inc'] = this.getInc(this.testGL);
            this.features['gpu'] = this.getGpu(this.testGL);
        }

        var jsFontsDetector = new JsFontsDetector();
        this.features['jsFonts'] = jsFontsDetector.testAllFonts().join('_');

        this.features['timezone'] = new Date().getTimezoneOffset();

        this.features['resolution'] = this.getResolution();

        this.features['plugins'] = this.getPlugins();

        this.features['cookie'] = navigator.cookieEnabled;

        this.features['localstorage'] = this.checkLocalStorage();

        this.features['adBlock'] = document.getElementById('ad') == null ? 'Yes' : 'No';

        this.features['audio'] = this.audioFingerPrinting();

        this.features['doNotTrack'] = this.getDoNotTrack();

        cvs_test = CanvasTest();
        // here we assume that the ID for canvas is 2
        // ===========================================
        // Maybe dangerous for later usage
        // ===========================================
        var cvs_dataurl = cvs_test.toDataURL('image/png', 1.0);

        this.features['image_b64'] = "imageBase64=" + encodeURIComponent(cvs_dataurl);

        this.features['canvastest'] = calcSHA1(cvs_dataurl);

        this.features['cpucores'] = this.getCPUCores();

        try {
            this.features['langsDetected'] = get_writing_scripts().join('_');
        } catch (e) {
        }
        this.features['touchSupport'] = this.getTouchSupport();

        /*if (this.features['WebGL'] == true) {
            var syncTest = new WebGlTest(this);
            syncTest.begin();
        }*/

        setTimeout(this.run_cc_fp, 1000, this, cb, cookie);

    }

    this.finished = false;

    //INSERTION OF AUDIOFINGERPRINT CODE
    // Performs fingerprint as found in https://www.cdn-net.com/cc.js
    this.run_cc_fp = function (collector, cb, cookie) {
        var cc_output = [];
        var audioCtx = new (window.AudioContext || window.webkitAudioContext),
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

        collector.features['ccaudio'] = "test";

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
            results = cc_output.slice(0, 30);
            collector.features['ccaudio'] = results.join('_');

            setTimeout(collector.run_hybrid_fp, 50, collector, cb, cookie);
        };
        oscillator.start(0);
    }


    // Performs a hybrid of cc/pxi methods found above
    // pass _this here because we need to use delay
    this.run_hybrid_fp = function (collector, cb, cookie) {
        var hybrid_output = [];
        var audioCtx = new (window.AudioContext || window.webkitAudioContext),
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
            collector.features['hybridaudio'] = hybrid_output.slice(0, 30).join('_');

            cb(collector.features, cookie);
        };
        oscillator.start(0);
    }

    //END INSERTION OF AUDIOFINGERPRINT CODE
    this.nextID = 0;
    this.getID = function () {
        if (this.finished) {
            throw "Can't generate ID anymore";
            return -1;
        }
        return this.nextID++;
    }

    this.getIDs = function (numIDs) {
        var idList = [];
        for (var i = 0; i < numIDs; ++i) {
            idList.push(this.getID());
        }
        return idList;
    }
};

/* Converts the charachters that aren't UrlSafe to ones that are and
   removes the padding so the base64 string can be sent
   */
Base64EncodeUrlSafe = function (str) {
    return str.replace(/\+/g, '-').replace(/\//g, '_').replace(/\=+$/, '');
};

stringify = function (array) {
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

//example of send install request
//set the features in json format, please set the cookie first
//nothing return by install API
function installCallback (features, cookie) {
    //set Cookie here
    if (typeof cookie != 'undefined') {
        features['label'] = cookie;
    }

    var data = JSON.stringify(features);

    var xhttp = new XMLHttpRequest();
    var url = ip_address + "/install.php";
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            console.log(this.responseText);
        }
    };
    xhttp.open("POST", url, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.send(data);
}

//example of send distance request
//set the features in json format
//return similarity,cookie. If there is nothing match, return NULL,
function distanceCallback (features) {
    var xhttp = new XMLHttpRequest();
    var url = ip_address + "/distance.php";
    var data = JSON.stringify(features);
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            console.log(this.responseText);
        }
    };
    xhttp.open("POST", url, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.send(data);

}

//example of print fingerprint
function fingerprintCallback (features) {
    console.log(Base64EncodeUrlSafe(JSON.stringify(features)));
}

//example of getting features and then sending install request
function install(cookie) {
    var collector = new Collector();
    //collector.syncTest(installCallback);
    collector.syncTest(installCallback, cookie);
}

//example of getting features and then sending distance request
function distance() {
    var collector = new Collector();
    collector.syncTest(distanceCallback);
}

//example of getting features and then printing the fingerprint
function fingerprint() {
    var collector = new Collector();
    collector.syncTest(fingerprintCallback);
}


