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

Vue.component('m3u-sel', {
    props: ['progs', 'id', 'lbl'],
    template: '#m3u-select',
    delimiters: ['${', '}'],
    methods: {
        onSelList: function () {
            sel = []
            opts = window[this.id].options
            for (let opt of opts) 
                if (opt.selected) 
                    sel.push({value: opt.value, title: opt.text})
            this.$emit('input',sel)
        }
    }
})


Vue.component('m3u-buttons', {
    props: ['buttons'],
    template: '#m3u-buttons',
    delimiters: ['${', '}']
})

Vue.component('m3u-prg', {
    data: function() {
        return {
            dt : new Date()
            //func_arr: [this.prev, this.now, this.next]
        }
    },
    props: ['spans', 'selected'],
    template: '#m3u-prg',
    delimiters: ['${', '}'],
    asyncComputed: {
        prg: {
            async get() {
                let jsn = {};
                jsn["date"] = this.dt.toISOString();
                jsn["name"] = this.selected.title;
                jss = JSON.stringify(jsn);
                const response = await fetch('/m3u/select', {
                    method: 'post',
                    headers: {
                        'Content-Type': 'application/json;charset=utf-8'
                    },
                    body: jss
                })
                const rsp = await response.json();
                if (rsp["start"] === "") {
                    spans.style.display = "none";
                    return { start: "", stop: "", tm: "", title: "", desc: "" };
                }
                let dstart = new Date(rsp["start"])
                let dstop = new Date(rsp["stop"])
                let tm = dstart.toTimeString().slice(0, 5) + " - " + dstop.toTimeString().slice(0, 5)
                delete dstart
                delete dstop
                spans.style.display = "block";
                return { start: rsp["start"], stop: rsp["stop"], tm: tm, title: rsp["title"], desc: rsp["desc"] }
            },
            default() {
                return { start: "", stop: "", tm: "", title: "", desc: "" };
            }
        }
    },
    methods: {
        span_click: function(ind) {
            var dict = {0: this.prev, 1: this.now, 2: this.next};
            dict[ind]();
        },
        prev: function() {
            t = new Date(this.prg.start);
            t.setMinutes(t.getMinutes() - 1);
            this.dt = t;
        },
        now: function() {
            this.dt = new Date();
        },
        next: function() {
            t = new Date(this.prg.stop);
            t.setMinutes(t.getMinutes() + 1);
            this.dt = t;
        }
    }
})

m3u_vue = new Vue({
    el: '#m3u',
    data: {
        selected: selected,
        s_buttons: buttons1,
        d_buttons: buttons2,
        spans: nav_span,
        s_lbl: label1,
        s_id: 'Sel',
        s_progs: m3u,
        s_selected: [],
        d_lbl: label2,
        d_id: 'RSel',
        d_progs: mym3u,
        d_selected: [],
        chk: false
    },
    delimiters: ['${', '}'],
    watch: {
        s_selected() {
            this.selected = this.s_selected[0];
            if(ext.checked) this.selected.value = "iptv:" + this.selected.value;
            else playc(this.selected);
            //get_epg(this.selected.title);
        },
        d_selected() {
            this.selected = this.d_selected[0];
            if(ext.checked) this.selected.value = "iptv:" + this.selected.value;
            else playc(this.selected);
            //get_epg(this.selected.title);
        },
        chk() {
            if (this.chk) {
              video.pause();
              video.hidden = true;
              this.selected.value = "iptv:" + this.selected.value;
            }
            else {
              video.hidden = false;
              this.selected.value = this.selected.value.substr(5);
            }
        }
    },
    methods: {
        s_button_click: function(ind) {
            var dict = {0: this.move, 1: this.unselect};
            dict[ind]();
        },
        d_button_click: function(ind) {
            var dict = {0: this.up, 1: this.down, 2: this.delete, 3: this.save};
            dict[ind]();
        },
        move: function() {
            let opts = Sel.options;
            for (let opt of opts) 
            if (opt.selected) 
                RSel.add(opt.cloneNode(true));
        },
        unselect: function() {
            let opts = Sel.options;
            for (let opt of opts) 
            if (opt.selected) 
                opt.selected = false;
            opts = RSel.options;
            for (let opt of opts) 
            if (opt.selected) 
                opt.selected = false;
        },
        up: function() {
            let n = RSel.selectedIndex;
            let opt = RSel.item(n);
            RSel.remove(n);
            RSel.add(opt,n-1);
        },
        down: function() {
            let n = RSel.selectedIndex;
            let opt = RSel.item(n);
            RSel.remove(n);
            RSel.add(opt,n+1);
        },
        delete: function() {
            let opts = RSel.options;
            for (let i = 0; i < opts.length; i++) {
                if (opts[i].selected) {
                    RSel.remove(i);
                    i--;
                }
            }
        },
        save: function() {
            let opts = RSel.options;
            let jsn = {};
            for (let opt of opts) {
                if (opt.disabled) continue;
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
                if (response.redirected) window.location.href = response.url;
                else response.text().then(function(myText){alert(myText);})
            })
        }
    }
})
