function getInstalledFonts_usingFlash(cb) {
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
    res = {};
    res['jsFonts'] = fonts.toString();
    console.log(res);
    cb(res);
  };
  var id = "flashfontfp";
  var node = document.createElement("div");
  node.setAttribute("id", id);
  document.body.appendChild(node);
  var flashvars = { onReady: hiddenCallback};
  var flashparams = { allowScriptAccess: "always", menu: "false" };
  swfobject.embedSWF("static/FontList.swf", id, "1", "1", "9.0.0", false, flashvars, flashparams, {});    
}
