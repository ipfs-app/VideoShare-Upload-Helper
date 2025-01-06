<template>
  <div class="container">
    <div class="row">
      <div class="col-2">
        日期
        <select class="form-select" v-model="video_select" @change="video_change">
          <option v-for="video in video_list" :value="video.date">{{ video.date }}</option>
        </select>
      </div>
      <div class="col-8">
        视频
        <select class="form-select" v-model="video_select2" @change="video_change2">
          <option v-for="video in video_list2" :value="video.id">{{ video.id }} [ {{ video.title }} ]</option>
        </select>
      </div>
      <div class="col-2 d-grid">
        <button type="button" class="btn btn-success" v-on:click="create_video">新建视频</button>
      </div>
    </div>
    <div class="row text-center setpdev">
      <div :class="'col-3 '+css1">
        setp1: 填写资料
      </div>
      <div :class="'col-1 '+css2">
        >>
      </div>
      <div :class="'col-3 '+css2">
        setp2: 等待上传
      </div>
      <div :class="'col-1 '+css3">
        >>
      </div>
      <div :class="'col-3 '+css3">
        setp3: 查看视频
      </div>
    </div>
    <div class="row">
      <div class="col-12" v-if="state=='notReady'">
        <h2>setp1: 填写资料</h2>
        <div class="mb-3">
          <label for="videofile" class="form-label">视频文件：</label>
          <input class="form-control" type="file" id="videofile" ref="videofile">
        </div>
        <div class="mb-3">
          <label for="coverfile" class="form-label">封面图：</label>
          <input class="form-control" type="file" id="coverfile" ref="coverfile">
        </div>
        <div class="mb-3">
          <label for="title" class="form-label">视频标题：</label>
          <input type="email" class="form-control" id="title" v-model="title">
        </div>
        <div class="mb-3">
          <label for="describe" class="form-label">简介：</label>
          <textarea class="form-control" id="describe" rows="3" v-model="describe"></textarea>
        </div>
        <button type="button" class="btn btn-success" @click="save_video">确认上传</button>
      </div>
      <div class="col-12" v-if="state=='progress'">
        <h2>setp2: 等待上传</h2>
        正在发布中... {{ progress_time }}
      </div>
      <div class="col-12" v-if="state=='ready'">
        <h2>setp3: 查看视频</h2>
        <div class="mb-3">
          <a :href="player+'#files.json='+json_hash" target="_blank">点击查看</a>
        </div>
        <div class="mb-3">
          files.json hash: {{ json_hash }}
        </div>
        <div class="mb-3">
          播放地址: https://ipfs.io{{ player }}#files.json={{ json_hash }}
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import Axios from 'axios'
import {ref} from 'vue'

const video_list = ref([])
const video_select = ref("")
const video_list2 = ref([])
const video_select2 = ref("")

const title = ref("")
const describe = ref("")
const videofile = ref(null)
const coverfile = ref(null)
const state = ref("")
const progress_time = ref("")
const json_hash = ref("")
const player = ref("")
const css1=ref("")
const css2=ref("")
const css3=ref("")
let local_video_list = JSON.parse(window.localStorage.getItem("video_list"))
if (!local_video_list) {
  local_video_list = []
}

video_list.value = local_video_list

let local_video_list2 = JSON.parse(window.localStorage.getItem("video_"+video_select.value))
if (!local_video_list2) {
  local_video_list2 = []
}
video_list2.value = local_video_list2
function create_video() {
  Axios.get('/create_video').then((res) => {
    if (!video_list.value.some(video => video.date === res.data.date)){
      video_list.value.push({"date": res.data.date})
      window.localStorage.setItem("video_list", JSON.stringify(video_list.value))
    }
    video_select.value = res.data.date

    let local_video_list2 = JSON.parse(window.localStorage.getItem("video_"+video_select.value))
    if (!local_video_list2) {
      local_video_list2 = []
    }
    video_list2.value = local_video_list2
    video_list2.value.push({"id": res.data.id, secret: res.data.secret, "title": ""})
    window.localStorage.setItem("video_"+res.data.date, JSON.stringify(video_list2.value))
    video_select2.value = res.data.id
    video_change2()
  })
}
function video_change(){
  video_list2.value = []
  let local_video_list2 = JSON.parse(window.localStorage.getItem("video_"+video_select.value))
  if (!local_video_list2) {
    local_video_list2 = []
  }
  video_list2.value = local_video_list2
  video_select2.value = video_list2.value[0].id
  video_change2()
}
function video_change2(){
  check_video()
}
function formatDateTime(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0'); // 月份从0开始，所以加1
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  const seconds = String(date.getSeconds()).padStart(2, '0');

  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}
function check_video(){
  
  Axios.get('/get_video?date='+video_select.value+'&id='+video_select2.value+'&secret='+video_list2.value.find(video => video.id === video_select2.value).secret).then((res) => {
    state.value = res.data.data.state
    switch (res.data.data.state) {
      case "notReady":
        title.value = res.data.data.title
        describe.value = res.data.data.describe
        css1.value = "setpdev_sel"
        css2.value = ""
        css3.value = ""
        break
      case "progress":
        progress_time.value = "启动时间: "+formatDateTime(new Date(res.data.data.startTime*1000))+" 运行时间: "+Math.round(Date.now()/1000 - res.data.data.startTime)+"s";
        setTimeout(check_video, 1000)
        css1.value = "setpdev_sel"
        css2.value = "setpdev_sel"
        css3.value = ""
        break
      case "ready":
        json_hash.value = res.data.data.json_hash
        player.value = res.data.data.player
        css1.value = "setpdev_sel"
        css2.value = "setpdev_sel"
        css3.value = "setpdev_sel"
        break
    }
  })
}

function save_video(){
  Axios.post('/save_video', {
    id: video_select2.value,
    date: video_select.value,
    secret: video_list2.value.find(video => video.id === video_select2.value).secret,
    title: title.value,
    describe: describe.value,
    video: videofile.value.files[0],
    cover: coverfile.value.files[0],
  },{
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }).then((res) => {
    video_list2.value.find(video => video.id === video_select2.value).title = title.value
    window.localStorage.setItem("video_"+video_select.value, JSON.stringify(video_list2.value))
    video_change2()
  })
}
</script>
<style scoped>
.setpdev > div {
  font-size: 2em;
  font-weight: bold;
  color: #999;
  transition-duration: 0.5s;
}
.setpdev > div.setpdev_sel{
  color: #008000;
}
</style>
