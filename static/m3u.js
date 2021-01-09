  /*function get_epg(ch, dt=null) {
    let jsn = {};
    if (dt == null) dt = new Date();
    jsn["date"] = dt.toISOString();
    jsn["name"] = ch;
    jss = JSON.stringify(jsn);
    fetch('/m3u/select', {
      method: 'post',
      headers: {
        'Content-Type': 'application/json;charset=utf-8'
      },
      body: jss
    }).then(function(response) {
      response.json().then(function(rsp) {
        //alert(rsp["start"])
        if (rsp["start"] === "") tm.innerHTML = prev.innerHTML = now.innerHTML = next.innerHTML = "";
        else {
          let start = new Date(rsp["start"]);
          let stop = new Date(rsp["stop"]); 
          tm.dataset.start = rsp["start"];
          tm.dataset.stop = rsp["stop"];
          tm.innerHTML = start.toTimeString().slice(0,5) + " - " + stop.toTimeString().slice(0,5);
          prev.innerHTML = "<<";
          now.innerHTML = "==";
          next.innerHTML = ">>";
        }
        ttl.innerHTML = rsp["title"];
        desc.innerHTML = rsp["desc"];
        delete start;
        delete stop; 
    })
    })
    delete nw;
  }*/

  function isMobile() {
    if( navigator.userAgent.match(/Android/i)
    || navigator.userAgent.match(/iPhone/i)
    || navigator.userAgent.match(/iPad/i)
    || navigator.userAgent.match(/iPod/i)) return true;
    return false;
  }

  function playc(sel) {
    var videoSrc = sel.value;
    if (Hls.isSupported()) {
      var hls = new Hls();
      hls.loadSource(videoSrc);
      hls.attachMedia(video);
      hls.on(Hls.Events.MANIFEST_PARSED, function() {
        video.play();
      });
    }
    else if (video.canPlayType('application/vnd.apple.mpegurl')) {
      video.src = videoSrc;
    }
  }
