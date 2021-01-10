const eventBus = new Vue()

Vue.component('m3u-sel', {
    data: function() {
        return {
            dict: { 'add': this.add, 'unselect': this.unselect, 'up': this.up, 'down': this.down, 
                    'delete': this.delete, 'save': this.save }
        }
    },
    props: ['progs', 'id', 'lbl', 'funcs'],
    template: '#m3u-select',
    delimiters: ['${', '}'],
    created: function() {
        eventBus.$on('to-do',this.to_do)
    },
    beforeDestroy: function() {
        eventBus.$off('to-do')
    },
    methods: {
        onSelList: function () {
            sel = []
            opts = window[this.id].options
            for (let opt of opts) 
                if (opt.selected) 
                    sel.push({value: opt.value, title: opt.text})
            this.$emit('input',sel)
        },
        to_do: function(func) {
            if (this.funcs.includes(func)) this.dict[func]();
        },
        add: function() {
            let sel = this.$refs['Select'];
            let opts = sel.options;
            for (let opt of opts) 
            if (opt.selected) 
                RSel.add(opt.cloneNode(true));
        },
        unselect: function() {
            let sel = this.$refs['Select'];
            let opts = sel.options;
            for (let opt of opts) 
            if (opt.selected) 
                opt.selected = false;
        },
        up: function() {
            let sel = this.$refs['Select'];
            let n = sel.selectedIndex;
            let opt = sel.item(n);
            sel.remove(n);
            sel.add(opt,n-1);
        },
        down: function() {
            let sel = this.$refs['Select'];
            let n = sel.selectedIndex;
            let opt = sel.item(n);
            sel.remove(n);
            sel.add(opt,n+1);
        },
        delete: function() {
            let sel = this.$refs['Select'];
            let opts = sel.options;
            for (let i = 0; i < opts.length; i++) {
                if (opts[i].selected) {
                    sel.remove(i);
                    i--;
                }
            }
        },
        save: function() {
            let sel = this.$refs['Select'];
            let opts = sel.options;
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


Vue.component('m3u-buttons', {
    props: ['buttons', 'funcs'],
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
        },
        d_selected() {
            this.selected = this.d_selected[0];
            if(ext.checked) this.selected.value = "iptv:" + this.selected.value;
            else playc(this.selected);
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
            var dict = {0: 'add', 1: 'unselect'};
            eventBus.$emit('to-do', dict[ind]);
        },
        d_button_click: function(ind) {
            var dict = {0: 'up', 1: 'down', 2: 'delete', 3: 'save'};
            eventBus.$emit('to-do', dict[ind]);
        },
    }
})
