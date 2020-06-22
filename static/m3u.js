function movec() {
    let opts = Sel.options;
    for (let opt of opts) 
      if (opt.selected) 
        RSel.add(opt.cloneNode(true));
  }

  function unselectc() {
    let opts = Sel.options;
    for (let opt of opts) 
      if (opt.selected) 
        opt.selected = false;
    opts = RSel.options;
    for (let opt of opts) 
      if (opt.selected) 
        opt.selected = false;
  }
  
  function savec() {
    let opts = RSel.options;
    let jsn = {};
    for (let opt of opts) {
      if (opt.text.startsWith("Выберите")) continue;
      jsn[opt.text] = opt.value;
    }
    jss = JSON.stringify(jsn);
    fetch('/m3u/save', {
      method: 'post',
      headers: {
        'Content-Type': 'application/json;charset=utf-8'
      },
      body: jss
    }).then(function(response) {
      response.text().then(function(myText){alert(myText);})
    })
  }

  function deletec() {
    let opts = RSel.options;
    for (let i = 0; i < opts.length; i++) {
      if (opts[i].selected) {
        RSel.remove(i)
        i--
      }
    }
    //for (let opt of opts) 
    //  if (opt.selected) 
    //    RSel.remove(opt.index);
    // RSel.remove(RSel.selectedIndex)
  }

  function upc() {
    let n = RSel.selectedIndex;
    let opt = RSel.item(n);
    RSel.remove(n);
    RSel.add(opt,n-1);
  }

  function downc() {
    let n = RSel.selectedIndex;
    let opt = RSel.item(n);
    RSel.remove(n);
    RSel.add(opt,n+1);
  }

  function onchangec(sel) {
    ref.text = sel.options[sel.selectedIndex].text;
    if( navigator.userAgent.match(/Android/i)
    || navigator.userAgent.match(/iPhone/i)
    || navigator.userAgent.match(/iPad/i)
    || navigator.userAgent.match(/iPod/i)) { ref.href = sel.value; }
    else { ref.href = "iptv:" + sel.value; }
    //ref.href = sel.value;
  }

  function playc() {
    /* video.target = Sel.value
    var player = videojs('video',{techOrder: ['flash', 'html5']});
    player.src(Sel.value);
    player.play() 
    let n = Sel.selectedIndex;*/
    var video = document.getElementById('video');
    // var videoSrc = 'https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8';
    var videoSrc = "http://127.0.0.1:8080/1"//Sel.value;
    if (Hls.isSupported()) {
      var hls = new Hls();
      hls.loadSource(videoSrc);
      hls.attachMedia(video);
      hls.on(Hls.Events.MANIFEST_PARSED, function() {
        video.play();
      });
    }
    // hls.js is not supported on platforms that do not have Media Source
    // Extensions (MSE) enabled.
    //
    // When the browser has built-in HLS support (check using `canPlayType`),
    // we can provide an HLS manifest (i.e. .m3u8 URL) directly to the video
    // element through the `src` property. This is using the built-in support
    // of the plain video element, without using hls.js.
    //
    // Note: it would be more normal to wait on the 'canplay' event below however
    // on Safari (where you are most likely to find built-in HLS support) the
    // video.src URL must be on the user-driven white-list before a 'canplay'
    // event will be emitted; the last video event that can be reliably
    // listened-for when the URL is not on the white-list is 'loadedmetadata'.
    else if (video.canPlayType('application/vnd.apple.mpegurl')) {
      video.src = videoSrc;
      video.addEventListener('loadedmetadata', function() {
        video.play();
      }); 
    }
  }
