<template>
  <div class="container">
    <div class="row">
      <div class="col-2">
        日期
        <select class="form-select" v-model="video_select">
          <option v-for="video in video_list" :value="video.date">{{ video.date }}</option>
        </select>
      </div>
      <div class="col-8">
        视频
        <select class="form-select">
          <option v-for="video in video_list2" :value="video.id">{{ video.id }} [ {{ video.title }} ]</option>
        </select>
      </div>
      <div class="col-2 d-grid">
        <button type="button" class="btn btn-success" v-on:click="create_video">新建视频</button>
      </div>
    </div>
    <div class="row">
      <div class="col-4">
        setp1: 填写资料
      </div>
      <div class="col-4">
        setp2: 等待上传
      </div>
      <div class="col-4">
        setp3: 查看视频
      </div>
    </div>
    <div class="row">
      <div class="col-12">
        <h2>setp1: 填写资料</h2>
        <div class="mb-3">
          <label for="videofile" class="form-label">视频文件：</label>
          <input class="form-control" type="file" id="videofile">
        </div>
        <div class="mb-3">
          <label for="coverfile" class="form-label">封面图：</label>
          <input class="form-control" type="file" id="coverfile">
        </div>
        <div class="mb-3">
          <label for="title" class="form-label">视频标题：</label>
          <input type="email" class="form-control" id="title">
        </div>
        <div class="mb-3">
          <label for="describe" class="form-label">简介：</label>
          <textarea class="form-control" id="describe" rows="3"></textarea>
        </div>
        <button type="button" class="btn btn-success">确认上传</button>
      </div>
      <div class="col-12">
        <h2>setp2: 等待上传</h2>
        正在发布中... 00:05:32
      </div>
      <div class="col-12">
        <h2>setp3: 查看视频</h2>
        <div class="mb-3">
          <a href="#">点击查看</a>
        </div>
        <div class="mb-3">
          files.json hash:
        </div>
        <div class="mb-3">
          播放地址: https://ipfs.io/ipfs/bs1/#files.json=bs123123
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import Axios from 'axios'
import {ref, onMounted, shallowRef, markRaw} from 'vue'

const video_list = ref([])
const video_select = ref("")
const video_list2 = ref([])
let local_video_list = JSON.parse(window.localStorage.getItem("video_list"))
if (!video_list) {
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
    console.log(res.data);
  })

}

</script>
<style scoped>

</style>
