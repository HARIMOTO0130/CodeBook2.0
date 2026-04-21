<template>
  <div class="video-list-container">
    <div class="video-list-header">
      <h3>教学视频</h3>
      <div class="video-count">{{ videos.length }} 个视频</div>
    </div>
    <div class="video-list-content">
      <div
        v-for="(video, index) in videos"
        :key="video.id || index"
        class="video-item"
        @click="playVideo(video)"
      >
        <div class="video-thumbnail">
          <img :src="getVideoThumbnail(video)" :alt="video.title" />
          <div class="video-duration">{{ video.duration || '00:00' }}</div>
        </div>
        <div class="video-info">
          <div class="video-title">{{ video.title }}</div>
          <div class="video-meta">
            <span class="video-format">{{ video.video_format || 'MP4' }}</span>
            <span class="video-size">{{ video.file_size || '未知' }}</span>
          </div>
        </div>
        <div class="video-actions">
          <button class="play-btn" @click.stop="playVideo(video)">
            <span class="play-icon">▶</span>
          </button>
        </div>
      </div>
      <div v-if="videos.length === 0" class="empty-videos">
        <p>该章节暂无视频资源</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'VideoList',
  props: {
    videos: {
      type: Array,
      default: () => []
    }
  },
  setup(props, { emit }) {
    const showVideo = ref(false)
    const currentVideo = ref(null)

    // 获取视频缩略图
    const getVideoThumbnail = (video) => {
      // 这里可以根据视频URL生成缩略图，或者使用默认图片
      return `https://picsum.photos/300/180?random=${video.id || Math.random()}`
    }

    // 播放视频
    const playVideo = (video) => {
      currentVideo.value = video
      emit('playVideo', video)
    }

    return {
      showVideo,
      currentVideo,
      getVideoThumbnail,
      playVideo
    }
  }
}
</script>

<style scoped>
.video-list-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin: 20px 0;
}

.video-list-header {
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.video-list-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.video-count {
  font-size: 14px;
  color: #909399;
}

.video-list-content {
  padding: 16px;
}

.video-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  transition: all 0.2s ease;
  cursor: pointer;
  margin-bottom: 12px;
}

.video-item:hover {
  background-color: #f5f7fa;
}

.video-thumbnail {
  position: relative;
  width: 120px;
  height: 72px;
  border-radius: 6px;
  overflow: hidden;
  margin-right: 16px;
  flex-shrink: 0;
}

.video-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-duration {
  position: absolute;
  bottom: 4px;
  right: 4px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
}

.video-info {
  flex: 1;
  min-width: 0;
}

.video-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.video-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #909399;
}

.video-actions {
  margin-left: 12px;
  flex-shrink: 0;
}

.play-btn {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.play-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(240, 147, 251, 0.4);
}

.play-icon {
  font-size: 12px;
  margin-left: 1px;
}

.empty-videos {
  text-align: center;
  padding: 40px 20px;
  color: #909399;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .video-list-container {
    margin: 16px 0;
  }
  
  .video-list-header {
    padding: 16px;
  }
  
  .video-list-header h3 {
    font-size: 16px;
  }
  
  .video-list-content {
    padding: 12px;
  }
  
  .video-item {
    padding: 10px;
    margin-bottom: 10px;
  }
  
  .video-thumbnail {
    width: 100px;
    height: 60px;
    margin-right: 12px;
  }
  
  .video-title {
    font-size: 13px;
  }
  
  .video-meta {
    font-size: 11px;
    gap: 8px;
  }
}
</style>