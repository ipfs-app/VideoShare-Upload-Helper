<template>
  <div class="container">
    <div class="row">
      <div class="col-2">
        <a href="index.html">最近更新</a>
        <a href="upload.html">上传页面</a>
      </div>
    </div>
    <div class="row">
      <table class="table">
        <tbody>
          <tr>
            <th>日期</th>
            <th>标题</th>
            <th>点击观看</th>
          </tr>
          <tr v-for="video in video_list">
            <th>{{ video.date }}</th>
            <td>{{ video.title }}</td>
            <td><a :href="player+'#files.json='+video.json_hash">播放</a></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
<script setup>
import Axios from 'axios'
import {ref, onMounted, shallowRef, markRaw} from 'vue'

const video_list = ref([])
const player = ref("")

Axios.get('/latest').then((res) => {
  video_list.value = res.data.data
  player.value = res.data.player
})
</script>
<style scoped>
</style>
