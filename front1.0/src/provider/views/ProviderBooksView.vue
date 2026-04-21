<template>
  <ProviderLayout>
    <div class="provider-books">
      <!-- 顶部操作区：搜索 + 新建按钮 -->
      <div class="toolbar">
        <div class="search-group">
          <input
            v-model="keyword"
            type="text"
            class="search-input"
            placeholder="搜索书名、作者或标签..."
            @keyup.enter="loadBooks"
          />
          <button class="search-button" @click="loadBooks">🔍 搜索</button>
          <button v-if="keyword && hasSearched" class="search-button back-button" @click="resetSearch">🔙 返回</button>
        </div>

        <div class="toolbar-actions">
          <button class="btn" @click="loadBooks">刷新</button>
          <button class="btn btn-secondary" @click="openUploadDialog">📁 上传教材文件</button>
          <button class="btn btn-primary" @click="openCreateDialog">＋ 新建教材</button>
        </div>
      </div>

      <div class="layout">
        <!-- 左侧：书籍列表 -->
        <div class="books-list">
          <h3 class="section-title">教材列表</h3>

          <div v-if="loading" class="empty-tip">正在加载教材...</div>
          <div v-else-if="books.length === 0" class="empty-tip">暂无教材，请先创建。</div>

          <div
            v-for="book in books"
            :key="book.id"
            class="book-card"
            @click="selectBook(book, $event)"
            :class="{ active: currentBook && currentBook.id === book.id }"
          >
            <div class="book-cover" :style="{ backgroundColor: getCoverColor(book.id) }">
              <span v-if="!book.cover">{{ (book.title || '书').charAt(0) }}</span>
              <img v-else :src="book.cover" :alt="book.title" />
              <div v-if="book.permission_status" class="permission-badge" :class="book.permission_status">
                {{ getPermissionStatusText(book.permission_status) }}
              </div>
            </div>
            <div class="book-info">
              <div class="book-title-row">
                <h4 class="book-title">{{ book.title || '未命名书籍' }}</h4>
                <span v-if="book.is_archived || false" class="status-tag archived">已归档</span>
                <span v-if="book.permission_status && book.permission_status !== 'open'" class="status-tag" :class="book.permission_status">
                  {{ getPermissionStatusText(book.permission_status) }}
                </span>
              </div>
              <p class="book-author">作者：{{ book.author || '未知' }}</p>
              <p class="book-desc">{{ book.description || '暂无简介' }}</p>
              <div class="book-meta">
                <span class="meta-item">章节：{{ book.chapter_count || 0 }}</span>
                <span class="meta-item">标签：{{ (book.tag_objects || book.tag_list || []).length }}</span>
              </div>
              <div class="tag-row" v-if="(book.tag_objects && book.tag_objects.length) || (book.tag_list && book.tag_list.length)">
                <span
                  v-for="tag in (book.tag_objects && book.tag_objects.length ? book.tag_objects : book.tag_list)"
                  :key="tag"
                  class="tag"
                >
                  {{ tag }}
                </span>
              </div>
            </div>
          </div>

          <!-- 分页导航 -->
          <div v-if="totalPages > 1" class="pagination">
            <div class="pagination-info">
              共 {{ totalBooks }} 本书，第 {{ currentPage }} / {{ totalPages }} 页
            </div>
            <div class="pagination-controls">
              <button 
                class="pagination-btn" 
                @click="goToFirstPage($event)" 
                :disabled="currentPage === 1"
              >
                首页
              </button>
              <button 
                class="pagination-btn" 
                @click="goToPrevPage($event)" 
                :disabled="currentPage === 1"
              >
                上一页
              </button>
              
              <!-- 页码按钮 -->
              <span 
                v-for="page in visiblePages" 
                :key="page"
                class="pagination-page"
                :class="{ active: page === currentPage }"
                @click="goToPage(page, $event)"
              >
                {{ page }}
              </span>
              
              <button 
                class="pagination-btn" 
                @click="goToNextPage($event)" 
                :disabled="currentPage === totalPages"
              >
                下一页
              </button>
              <button 
                class="pagination-btn" 
                @click="goToLastPage($event)" 
                :disabled="currentPage === totalPages"
              >
                末页
              </button>
            </div>
          </div>
        </div>

        <!-- 右侧：选中书籍详情 + 版本列表 -->
        <div class="sidebar" v-if="currentBook">
          <h3 class="section-title">版本与状态</h3>

          <div class="book-summary">
            <h4>{{ currentBook.title }}</h4>
            <p class="book-author">作者：{{ currentBook.author || '未知' }}</p>
            <p class="book-desc">{{ currentBook.description || '暂无简介' }}</p>
          </div>

          <div class="versions-header">
            <span>版本历史</span>
            <button class="btn btn-primary btn-sm" @click="goToBookDetail">查看详情</button>
          </div>

          <div v-if="versionsLoading" class="empty-tip small">正在加载版本...</div>
          <div v-else-if="versions.length === 0" class="empty-tip small">暂无版本记录。</div>

          <ul v-else class="version-list">
            <li 
              v-for="(ver, index) in versions" 
              :key="ver?.id || index" 
              class="version-item"
              @click="goToVersionDetail(ver)"
              style="cursor: pointer;"
            >
              <div class="version-main">
                <span class="version-tag">v{{ ver?.version_number || 'N/A' }}</span>
                <span class="version-title">{{ ver?.title || '未知' }}</span>
              </div>
              <div class="version-meta">
                <span>{{ formatTime(ver?.created_at) }}</span>
                <span v-if="ver?.created_by">创建人：{{ ver.created_by }}</span>
              </div>
              <p class="version-comment" v-if="ver?.comment">{{ ver.comment }}</p>
            </li>
          </ul>

          <!-- 操作按钮区域 -->
          <div class="book-actions">
            <button class="btn" :class="currentBook.permission_status === 'locked' ? 'btn-primary' : 'btn-secondary'" @click="toggleBookLock(currentBook)">
              {{ currentBook.permission_status === 'locked' ? '🔓 解锁' : '🔒 加锁' }}
            </button>
            <button class="btn btn-secondary" @click="openPermissionRequests(currentBook)">📋 权限申请</button>
            <button class="btn btn-secondary" @click="openUserPermissions(currentBook)">👥 用户权限</button>
            <button class="btn btn-secondary" @click="viewLockLogs(currentBook)">📜 加锁日志</button>
            <button class="btn btn-danger" @click="openDeleteDialog">删除教材</button>
          </div>
        </div>
      </div>

      <!-- 新建教材弹窗 -->
      <div v-if="showCreate" class="modal-overlay" @click.self="showCreate = false">
        <div class="modal">
          <div class="modal-header">
            <h3>新建教材</h3>
            <button class="close-btn" @click="showCreate = false">×</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label">教材名称</label>
              <input v-model="createForm.title" type="text" class="input" placeholder="请输入教材名称" />
            </div>
            <div class="form-group">
              <label class="form-label">副标题（可选）</label>
              <input v-model="createForm.subtitle" type="text" class="input" placeholder="教材的副标题" />
            </div>
            <div class="form-group">
              <label class="form-label">作者</label>
              <input v-model="createForm.author" type="text" class="input" placeholder="作者姓名" />
            </div>
            <div class="form-group">
              <label class="form-label">ISBN（可选）</label>
              <input v-model="createForm.isbn" type="text" class="input" placeholder="国际标准书号" />
            </div>
            <div class="form-group">
              <label class="form-label">封面上传（可选）</label>
              <input type="file" class="input" accept="image/*" @change="handleCoverUpload" />
            </div>
            <div class="form-group">
              <label class="form-label">简介</label>
              <textarea v-model="createForm.description" class="input" rows="2" placeholder="简要描述教材内容"></textarea>
            </div>
            <div class="form-group">
              <label class="form-label">详细介绍（可选）</label>
              <textarea v-model="createForm.introduction" class="input" rows="4" placeholder="教材的详细介绍"></textarea>
            </div>
            <div class="form-group">
              <label class="form-label">语言（可选）</label>
              <input v-model="createForm.language" type="text" class="input" placeholder="如 Python / JavaScript" />
            </div>
            <div class="form-group">
              <label class="form-label">分类（可选）</label>
              <input v-model="createForm.categories" type="text" class="input" placeholder="多个分类用逗号分隔" />
            </div>
            <div class="form-group">
              <label class="form-label">标签（可选）</label>
              <input v-model="createForm.tags" type="text" class="input" placeholder="多个标签用逗号分隔" />
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn" @click="showCreate = false">取消</button>
            <button class="btn btn-primary" @click="submitCreate" :disabled="creating">
              {{ creating ? '创建中...' : '保存' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 删除教材确认弹窗 -->
      <div v-if="showDelete" class="modal-overlay" @click.self="showDelete = false">
        <div class="modal">
          <div class="modal-header">
            <h3>确认删除</h3>
            <button class="close-btn" @click="showDelete = false">×</button>
          </div>
          <div class="modal-body">
            <p class="delete-warning">
              您确定要删除教材 <span class="delete-book-title">{{ currentBook?.title }}</span> 吗？
            </p>
            <p class="delete-info">
              删除操作不可恢复，所有相关的版本信息也将被删除。
            </p>
          </div>
          <div class="modal-footer">
            <button class="btn" @click="showDelete = false">取消</button>
            <button class="btn btn-danger" @click="submitDelete" :disabled="deleting">
              {{ deleting ? '删除中...' : '确认删除' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 上传教材文件弹窗 -->
      <div v-if="showUpload" class="modal-overlay" @click.self="showUpload = false">
        <div class="modal">
          <div class="modal-header">
            <h3>上传教材文件</h3>
            <button class="close-btn" @click="showUpload = false">×</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label">教材名称</label>
              <input v-model="uploadForm.title" type="text" class="input" placeholder="请输入教材名称" />
            </div>
            <div class="form-group">
              <label class="form-label">作者</label>
              <input v-model="uploadForm.author" type="text" class="input" placeholder="作者姓名" />
            </div>
            <div class="form-group">
              <label class="form-label">语言（可选）</label>
              <input v-model="uploadForm.language" type="text" class="input" placeholder="如 Python / JavaScript" />
            </div>
            <div class="form-group">
              <label class="form-label">选择文件</label>
              <input 
                type="file" 
                class="input" 
                accept=".pdf,.docx,.md,.epub"
                @change="handleFileUpload"
              />
              <div class="file-info" v-if="uploadForm.file">
                已选择: {{ uploadForm.file.name }} ({{ formatFileSize(uploadForm.file.size) }})
              </div>
              <div class="supported-formats">
                支持格式: PDF, DOCX, MD, EPUB
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">分类（可选）</label>
              <input v-model="uploadForm.categories" type="text" class="input" placeholder="多个分类用逗号分隔" />
            </div>
            <div class="form-group">
              <label class="form-label">标签（可选）</label>
              <input v-model="uploadForm.tags" type="text" class="input" placeholder="多个标签用逗号分隔" />
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn" @click="showUpload = false">取消</button>
            <button class="btn btn-primary" @click="submitUpload" :disabled="uploading || !uploadForm.file">
              {{ uploading ? '上传中...' : '上传并解析' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 权限申请审核弹窗 -->
      <div v-if="showPermissionRequests" class="modal-overlay" @click.self="showPermissionRequests = false">
        <div class="modal">
          <div class="modal-header">
            <h3>权限申请审核</h3>
            <button class="close-btn" @click="showPermissionRequests = false">×</button>
          </div>
          <div class="modal-body">
            <div v-if="permissionRequestsLoading" class="empty-tip">正在加载权限申请...</div>
            <div v-else-if="permissionRequests.length === 0" class="empty-tip">暂无权限申请</div>
            <div v-else class="permission-requests-list">
              <div
                v-for="request in permissionRequests"
                :key="request.id"
                class="permission-request-item"
              >
                <div class="request-header">
                  <span class="request-user">{{ request.user }}</span>
                  <span class="request-status" :class="request.status">{{ getPermissionStatusText(request.status) }}</span>
                </div>
                <div class="request-content">
                  <p class="request-reason">{{ request.reason }}</p>
                  <div class="request-meta">
                    <span>{{ formatTime(request.created_at) }}</span>
                    <span v-if="request.reviewed_at">审核时间: {{ formatTime(request.reviewed_at) }}</span>
                    <span v-if="request.reviewer">审核人: {{ request.reviewer }}</span>
                  </div>
                </div>
                <div v-if="request.status === 'pending'" class="request-actions">
                  <button class="btn btn-primary" @click="reviewPermissionRequest(request, 'approved')">同意</button>
                  <button class="btn btn-danger" @click="reviewPermissionRequest(request, 'rejected')">拒绝</button>
                </div>
                <div v-else-if="request.review_comment" class="review-comment">
                  <strong>审核意见:</strong> {{ request.review_comment }}
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn" @click="showPermissionRequests = false">关闭</button>
          </div>
        </div>
      </div>

      <!-- 加锁弹窗 -->
      <div v-if="showLockDialog" class="modal-overlay" @click.self="showLockDialog = false">
        <div class="modal">
          <div class="modal-header">
            <h3>教材加锁</h3>
            <button class="close-btn" @click="showLockDialog = false">×</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label">锁定原因（可选）</label>
              <textarea v-model="lockForm.reason" class="input" rows="3" placeholder="请输入锁定原因，如：内容更新维护中"></textarea>
            </div>
            <div class="form-group">
              <label class="form-label">锁定期限</label>
              <select v-model="lockForm.duration" class="input">
                <option value="1小时">1小时</option>
                <option value="3小时">3小时</option>
                <option value="6小时">6小时</option>
                <option value="12小时">12小时</option>
                <option value="1天">1天</option>
                <option value="3天">3天</option>
                <option value="7天" selected>7天</option>
                <option value="2周">2周</option>
                <option value="1个月">1个月</option>
                <option value="3个月">3个月</option>
                <option value="永久">永久</option>
              </select>
            </div>
            <div class="lock-tips">
              <p class="tip-text">💡 提示：加锁后，学生将无法访问该教材，直到您手动解锁或到期自动解锁</p>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn" @click="showLockDialog = false">取消</button>
            <button class="btn btn-primary" @click="submitLock">确认加锁</button>
          </div>
        </div>
      </div>

      <!-- 加锁日志弹窗 -->
      <div v-if="showLockLogsDialog" class="modal-overlay" @click.self="showLockLogsDialog = false">
        <div class="modal" style="width: 600px;">
          <div class="modal-header">
            <h3>加锁日志</h3>
            <button class="close-btn" @click="showLockLogsDialog = false">×</button>
          </div>
          <div class="modal-body" style="max-height: 400px; overflow-y: auto;">
            <div v-if="lockLogsLoading" class="empty-tip">正在加载日志...</div>
            <div v-else-if="lockLogs.length === 0" class="empty-tip">暂无加锁日志</div>
            <div v-else class="lock-logs-list">
              <div
                v-for="log in lockLogs"
                :key="log.id"
                class="lock-log-item"
              >
                <div class="log-header">
                  <span class="log-action" :class="log.action">{{ getLockActionText(log.action) }}</span>
                  <span class="log-time">{{ formatTime(log.created_at) }}</span>
                </div>
                <div class="log-content">
                  <p v-if="log.reason"><strong>原因：</strong>{{ log.reason }}</p>
                  <p v-if="log.duration"><strong>时长：</strong>{{ log.duration }}</p>
                  <p><strong>操作人：</strong>{{ log.operator_username || '系统' }}</p>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn" @click="showLockLogsDialog = false">关闭</button>
          </div>
        </div>
    </div>
  </div>

  <!-- 用户权限管理弹窗 -->
  <div v-if="showUserPermissions" class="modal-overlay" @click.self="showUserPermissions = false">
    <div class="modal" style="width: 800px; max-width: 90vw;">
      <div class="modal-header">
        <h3>用户权限管理 - {{ currentPermissionBook?.title }}</h3>
        <button class="close-btn" @click="showUserPermissions = false">×</button>
      </div>
      <div class="modal-body">
        <div v-if="userPermissionsLoading" class="loading">
          <div class="spinner"></div>
          <p>加载中...</p>
        </div>
        <div v-else-if="userPermissions.length === 0" class="empty-state">
          <p>暂无用户权限记录</p>
        </div>
        <div v-else class="user-permissions-list">
          <table class="table">
            <thead>
              <tr>
                <th>用户</th>
                <th>权限状态</th>
                <th>创建时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="permission in userPermissions" :key="permission.id">
                <td>{{ permission.user_name || '未知用户' }}</td>
                <td>
                  <span :class="{
                    'status-badge': true,
                    'status-open': permission.status === 'open',
                    'status-locked': permission.status === 'locked'
                  }">
                    {{ getPermissionStatusText(permission.status) }}
                  </span>
                </td>
                <td>{{ formatTime(permission.created_at) }}</td>
                <td>
                  <button 
                    class="btn btn-sm" 
                    :class="permission.status === 'open' ? 'btn-danger' : 'btn-success'"
                    @click="toggleUserPermission(permission)"
                  >
                    {{ permission.status === 'open' ? '🔒 加锁' : '🔓 解锁' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-default" @click="showUserPermissions = false">关闭</button>
      </div>
    </div>
  </div>
  </ProviderLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import ProviderLayout from './ProviderLayout.vue'
import { providerApi } from '../api/index.js'

const router = useRouter()
const books = ref([])
const loading = ref(false)
const keyword = ref('')

// 分页相关状态
const currentPage = ref(1)
const totalPages = ref(1)
const totalBooks = ref(0)
const pageSize = ref(5)

// 搜索状态跟踪
const hasSearched = ref(false)

const currentBook = ref(null)
const versions = ref([])
const versionsLoading = ref(false)
// 新建教材相关状态
const showCreate = ref(false)
const creating = ref(false)
const createForm = ref({
  title: '',
  subtitle: '',
  author: '',
  isbn: '',
  description: '',
  introduction: '',
  language: '',
  categories: '',
  tags: '',
  cover: null,
})

// 删除教材相关状态
const showDelete = ref(false)
const deleting = ref(false)

// 文件上传相关状态
const showUpload = ref(false)
const uploading = ref(false)
const uploadForm = ref({
  title: '',
  author: '',
  language: '',
  file: null,
  fileType: '',
  categories: '',
  tags: '',
})

// 权限申请审核相关状态
const showPermissionRequests = ref(false)
const permissionRequests = ref([])
const permissionRequestsLoading = ref(false)

// 用户权限管理相关状态
const showUserPermissions = ref(false)
const userPermissions = ref([])
const userPermissionsLoading = ref(false)
const currentPermissionBook = ref(null)

const resetSearch = () => {
  keyword.value = ''
  currentPage.value = 1
  hasSearched.value = false
  loadBooks()
}

const loadBooks = async () => {
  loading.value = true
  try {
    // 构建请求参数，包括搜索关键词和分页信息
    const params = {
      search: keyword.value,
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    console.log('请求书籍列表的参数:', params)
    const data = await providerApi.listBooks(params)
    console.log('返回的书籍列表数据:', data)
    console.log('返回数据类型:', typeof data)
    console.log('返回数据是否有results:', 'results' in data)
    
    // 处理后端的分页响应
    if (data.results) {
      // 有分页信息的情况
      console.log('分页数据-结果数量:', data.results.length)
      console.log('分页数据-总数量:', data.count)
      console.log('分页数据-页码信息:', { next: data.next, previous: data.previous })
      
      books.value = data.results
      totalBooks.value = data.count
      totalPages.value = Math.ceil(data.count / pageSize.value)
      // DRF的分页响应不包含current_page字段，使用前端自己维护的currentPage
      // currentPage.value = data.current_page || currentPage.value
    } else {
      // 没有分页信息的情况（兼容旧版本）
      console.log('非分页数据-结果:', data)
      books.value = Array.isArray(data) ? data : []
      totalBooks.value = books.value.length
      totalPages.value = 1
      currentPage.value = 1
    }
    
    console.log('处理后的书籍列表:', books.value)
    console.log('书籍列表长度:', books.value.length)
    console.log('当前选中的书籍:', currentBook.value)
    
    // 检查currentBook是否在当前书籍列表中，如果不在则重置为null
    if (currentBook.value) {
      const bookExists = books.value.some(book => book.id === currentBook.value.id)
      if (!bookExists) {
        console.log('当前选中的书籍不在列表中，重置为null')
        currentBook.value = null
      }
    }
    
    // 自动选择第一本书（如果没有选中的书籍），但不自动跳转到详情页
    if (!currentBook.value && books.value.length > 0) {
      currentBook.value = books.value[0]
      console.log('自动选择的书籍:', currentBook.value)
      // 确保bookId有效再加载版本
      if (currentBook.value && currentBook.value.id && (typeof currentBook.value.id === 'number' && currentBook.value.id > 0 || typeof currentBook.value.id === 'string' && currentBook.value.id.trim() !== '')) {
        await loadVersions(currentBook.value.id)
      } else {
        console.error('自动选择的书籍ID无效:', currentBook.value?.id)
      }
    }
    
    // 更新搜索状态
    if (keyword.value) {
      hasSearched.value = true
    } else {
      hasSearched.value = false
    }
  } catch (e) {
    console.error('加载教材失败', e)
  } finally {
    loading.value = false
  }
}

const selectBook = async (book, event) => {
  // 阻止事件冒泡，避免触发其他点击事件
  if (event) {
    event.preventDefault()
    event.stopPropagation()
  }
  
  if (!book || !book.id) {
    console.error('无效的书籍对象:', book)
    return
  }
  
  // 更新当前选中的书籍和右侧栏显示
  currentBook.value = book
  
  // 加载版本信息
  if (book.id) {
    await loadVersions(book.id)
  }
  
  // 不自动跳转到详情页，保持当前页面
  // 如果需要跳转到详情页，可以使用：await router.push({ name: 'ProviderBookDetail', params: { id: book.id } })
}

const loadVersions = async (bookId) => {
  // 验证bookId是否有效
  // 注意：Django的AutoField主键从1开始，所以0不是有效的ID
  if (!bookId || (typeof bookId === 'number' && bookId <= 0) || (typeof bookId === 'string' && bookId.trim() === '')) {
    console.error('无效的bookId:', bookId)
    versions.value = []
    versionsLoading.value = false
    return
  }
  versionsLoading.value = true
  try {
    console.log('正在加载书籍版本，bookId:', bookId)
    const data = await providerApi.listVersions(bookId)
    versions.value = data
    console.log('版本加载成功，数量:', data.length)
  } catch (e) {
    console.error('加载版本失败，bookId:', bookId, '错误详情:', e)
    versions.value = []
  } finally {
    versionsLoading.value = false
  }
}

const openUploadDialog = () => {
  uploadForm.value = {
    title: '',
    author: '',
    language: '',
    file: null,
    fileType: '',
    categories: '',
    tags: '',
  }
  showUpload.value = true
}

const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    uploadForm.value.file = file
    // 自动检测文件类型
    const fileName = file.name.toLowerCase()
    if (fileName.endsWith('.pdf')) {
      uploadForm.value.fileType = 'pdf'
    } else if (fileName.endsWith('.docx')) {
      uploadForm.value.fileType = 'docx'
    } else if (fileName.endsWith('.md')) {
      uploadForm.value.fileType = 'md'
    } else if (fileName.endsWith('.epub')) {
      uploadForm.value.fileType = 'epub'
    }
    
    // 如果用户没有输入标题，自动使用文件名作为标题
    if (!uploadForm.value.title) {
      uploadForm.value.title = file.name.replace(/\.[^/.]+$/, '')
    }
  }
}

const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB'
  else return (bytes / 1048576).toFixed(1) + ' MB'
}

const openCreateDialog = () => {
  createForm.value = {
    title: '',
    subtitle: '',
    author: '',
    isbn: '',
    description: '',
    introduction: '',
    language: '',
    categories: '',
    tags: '',
    cover: null,
  }
  showCreate.value = true
}

const handleCoverUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    createForm.value.cover = file
  }
}

const submitCreate = async () => {
  if (!createForm.value.title) return
  creating.value = true
  try {
    // 准备表单数据，包括文件
    const formData = new FormData()
    formData.append('title', createForm.value.title)
    formData.append('subtitle', createForm.value.subtitle || '')
    formData.append('author', createForm.value.author || '')
    formData.append('isbn', createForm.value.isbn || '')
    formData.append('description', createForm.value.description || '')
    formData.append('introduction', createForm.value.introduction || '')
    formData.append('language', createForm.value.language || '')
    
    // 处理分类和标签
    if (createForm.value.categories) {
      const categories = createForm.value.categories.split(',').map(c => c.trim()).filter(c => c)
      categories.forEach(category => {
        formData.append('categories', category)
      })
    }
    if (createForm.value.tags) {
      const tags = createForm.value.tags.split(',').map(t => t.trim()).filter(t => t)
      tags.forEach(tag => {
        formData.append('tags', tag)
      })
    }
    
    // 处理封面文件
    if (createForm.value.cover) {
      formData.append('cover', createForm.value.cover)
    }
    
    await providerApi.createBook(formData)
    showCreate.value = false
    await loadBooks()
  } catch (e) {
    console.error('创建教材失败', e)
  } finally {
    creating.value = false
  }
}

// 打开删除确认弹窗
const openDeleteDialog = () => {
  if (currentBook.value) {
    showDelete.value = true
  }
}

// 提交删除请求
const submitUpload = async () => {
  if (!uploadForm.value.title || !uploadForm.value.author || !uploadForm.value.file) return
  uploading.value = true
  try {
    // 准备表单数据
    const formData = new FormData()
    formData.append('title', uploadForm.value.title)
    formData.append('author', uploadForm.value.author)
    formData.append('language', uploadForm.value.language || '')
    formData.append('file', uploadForm.value.file)
    
    // 处理分类和标签
    if (uploadForm.value.categories) {
      const categories = uploadForm.value.categories.split(',').map(c => c.trim()).filter(c => c)
      categories.forEach(category => {
        formData.append('categories', category)
      })
    }
    if (uploadForm.value.tags) {
      const tags = uploadForm.value.tags.split(',').map(t => t.trim()).filter(t => t)
      tags.forEach(tag => {
        formData.append('tags', tag)
      })
    }
    
    // 根据文件类型选择相应的API函数
    let response
    switch (uploadForm.value.fileType) {
      case 'pdf':
        response = await providerApi.uploadPDF(formData)
        break
      case 'docx':
        response = await providerApi.uploadDOCX(formData)
        break
      case 'md':
        response = await providerApi.uploadMD(formData)
        break
      case 'epub':
        response = await providerApi.uploadEPUB(formData)
        break
      default:
        throw new Error('不支持的文件类型')
    }
    
    showUpload.value = false
    await loadBooks()
  } catch (e) {
    console.error('上传教材失败', e)
  } finally {
    uploading.value = false
  }
}

const submitDelete = async () => {
  if (!currentBook.value) return
  deleting.value = true
  try {
    await providerApi.deleteBook(currentBook.value.id)
    showDelete.value = false
    // 清空当前选中的书籍和版本
    currentBook.value = null
    versions.value = []
    // 重新加载书籍列表
    await loadBooks()
  } catch (e) {
    console.error('删除教材失败', e)
  } finally {
    deleting.value = false
  }
}

const getCoverColor = (bookId) => {
  const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#F9CA24', '#6C5CE7', '#A29BFE']
  return colors[bookId % colors.length]
}

// 分页导航函数
const goToPage = (page, event) => {
  if (event) {
    event.preventDefault()
    event.stopPropagation()
  }
  if (page >= 1 && page <= totalPages.value && page !== currentPage.value) {
    currentPage.value = page
    loadBooks()
  }
}

const goToNextPage = (event) => {
  if (event) {
    event.preventDefault()
    event.stopPropagation()
  }
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    loadBooks()
  }
}

const goToPrevPage = (event) => {
  if (event) {
    event.preventDefault()
    event.stopPropagation()
  }
  if (currentPage.value > 1) {
    currentPage.value--
    loadBooks()
  }
}

const goToFirstPage = (event) => {
  if (event) {
    event.preventDefault()
    event.stopPropagation()
  }
  if (currentPage.value > 1) {
    currentPage.value = 1
    loadBooks()
  }
}

const goToLastPage = (event) => {
  if (event) {
    event.preventDefault()
    event.stopPropagation()
  }
  if (currentPage.value < totalPages.value) {
    currentPage.value = totalPages.value
    loadBooks()
  }
}

// 计算当前可见的页码
const visiblePages = computed(() => {
  const pages = []
  const maxVisible = 5 // 最多显示5个页码
  
  if (totalPages.value <= maxVisible) {
    // 如果总页数少于等于最大显示数，显示所有页码
    for (let i = 1; i <= totalPages.value; i++) {
      pages.push(i)
    }
  } else {
    // 否则显示当前页附近的页码
    const half = Math.floor(maxVisible / 2)
    let start = currentPage.value - half
    let end = currentPage.value + half
    
    if (start < 1) {
      start = 1
      end = maxVisible
    }
    
    if (end > totalPages.value) {
      end = totalPages.value
      start = end - maxVisible + 1
    }
    
    for (let i = start; i <= end; i++) {
      pages.push(i)
    }
  }
  
  return pages
})

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const d = new Date(timeStr)
  return d.toLocaleString()
}

// 权限状态相关方法
const getPermissionStatusText = (status) => {
  const statusMap = {
    open: '已开放',
    locked: '已加锁',
    requested: '申请中'
  }
  return statusMap[status] || status
}

// 加锁相关状态
const showLockDialog = ref(false)
const lockForm = ref({
  reason: '',
  duration: ''
})
const lockLogs = ref([])
const showLockLogsDialog = ref(false)
const lockLogsLoading = ref(false)

// 打开加锁弹窗
const openLockDialog = async (book) => {
  if (!book || !book.id) return
  currentBook.value = book
  lockForm.value = {
    reason: '',
    duration: '7天'
  }
  showLockDialog.value = true
}

// 执行加锁
const submitLock = async () => {
  if (!currentBook.value || !currentBook.value.id) return
  try {
    await providerApi.lockBook(currentBook.value.id, {
      reason: lockForm.value.reason,
      duration: lockForm.value.duration
    })
    showLockDialog.value = false
    await loadBooks()
  } catch (e) {
    console.error('加锁失败', e)
    alert('加锁失败: ' + (e.message || '未知错误'))
  }
}

// 执行解锁
const submitUnlock = async () => {
  if (!currentBook.value || !currentBook.value.id) return
  try {
    await providerApi.unlockBook(currentBook.value.id, {
      unlock_reason: '手动解锁'
    })
    await loadBooks()
  } catch (e) {
    console.error('解锁失败', e)
    alert('解锁失败: ' + (e.message || '未知错误'))
  }
}

// 切换书籍锁定状态（使用新的加锁/解锁API）
const toggleBookLock = async (book) => {
  if (!book || !book.id) return
  if (book.permission_status === 'locked') {
    currentBook.value = book
    await submitUnlock()
  } else {
    await openLockDialog(book)
  }
}

// 查看加锁日志
const viewLockLogs = async (book) => {
  if (!book || !book.id) return
  currentBook.value = book
  lockLogsLoading.value = true
  showLockLogsDialog.value = true
  try {
    lockLogs.value = await providerApi.getBookLockLogs(book.id)
  } catch (e) {
    console.error('加载加锁日志失败', e)
    lockLogs.value = []
  } finally {
    lockLogsLoading.value = false
  }
}

// 格式化加锁日志操作类型
const getLockActionText = (action) => {
  const actionMap = {
    lock: '加锁',
    unlock: '解锁',
    request_unlock: '申请解锁',
    approve_unlock: '批准解锁',
    reject_unlock: '拒绝解锁'
  }
  return actionMap[action] || action
}

// 打开权限申请列表
const openPermissionRequests = async (book) => {
  if (!book || !book.id) return
  currentPermissionBook.value = book
  permissionRequestsLoading.value = true
  try {
    const requests = await providerApi.listPermissionRequests(book.id)
    permissionRequests.value = requests
    showPermissionRequests.value = true
  } catch (e) {
    console.error('加载权限申请失败', e)
  } finally {
    permissionRequestsLoading.value = false
  }
}

// 打开用户权限管理弹窗
const openUserPermissions = async (book) => {
  if (!book || !book.id) return
  currentPermissionBook.value = book
  userPermissionsLoading.value = true
  try {
    const permissions = await providerApi.listUserPermissions(book.id)
    userPermissions.value = permissions
    showUserPermissions.value = true
  } catch (e) {
    console.error('加载用户权限失败', e)
  } finally {
    userPermissionsLoading.value = false
  }
}

// 切换用户权限状态
const toggleUserPermission = async (permission) => {
  try {
    const newStatus = permission.status === 'open' ? 'locked' : 'open'
    await providerApi.updateUserPermission(permission.id, { status: newStatus })
    // 更新本地状态
    permission.status = newStatus
  } catch (e) {
    console.error('更新用户权限失败', e)
  }
}

// 审核权限申请
const reviewPermissionRequest = async (request, status) => {
  try {
    await providerApi.reviewPermissionRequest(request.id, { status })
    // 重新加载权限申请列表
    if (currentPermissionBook.value) {
      const requests = await providerApi.listPermissionRequests(currentPermissionBook.value.id)
      permissionRequests.value = requests
    }
  } catch (e) {
    console.error('审核权限申请失败', e)
  }
}

// 跳转到书籍详情页
const goToBookDetail = () => {
  if (currentBook.value && currentBook.value.id) {
    router.push({ name: 'ProviderBookDetail', params: { id: currentBook.value.id } })
  }
}

// 跳转到版本详情页
const goToVersionDetail = (version) => {
  if (version && version.id && version.book) {
    router.push({ 
      name: 'ProviderBookVersionDetail', 
      params: { 
        bookId: version.book,
        versionId: version.id 
      } 
    })
  }
}

onMounted(() => {
  // 显式重置currentBook，避免之前的状态影响
  currentBook.value = null
  loadBooks()
})
</script>

<style scoped>
.provider-books {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 8px;
}

.search-group {
  display: flex;
  flex: 1;
}

.search-input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid #dcdfe6;
  border-radius: 4px 0 0 4px;
  font-size: 14px;
}

.search-button {
  padding: 10px 16px;
  border: none;
  background: #409eff;
  color: #fff;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
}

.toolbar-actions {
  display: flex;
  gap: 8px;
}

.layout {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
}

.books-list,
.sidebar {
  min-height: 200px;
}

.section-title {
  margin-bottom: 12px;
  font-size: 18px;
}

.book-card {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #f0f0f0;
  margin-bottom: 10px;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
}

.book-card:hover {
  background: #f9fafc;
}

.book-card.active {
  border-color: #409eff;
  background: #ecf5ff;
}

.book-cover {
  width: 56px;
  height: 80px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #fff;
  font-weight: bold;
}

.book-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 4px;
}

.book-info {
  flex: 1;
}

.book-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.book-title {
  margin: 0;
  font-size: 16px;
}

.book-author {
  margin: 2px 0 4px 0;
  font-size: 13px;
  color: #666;
}

.book-desc {
  margin: 0 0 4px 0;
  font-size: 13px;
  color: #777;
}

.book-meta {
  font-size: 12px;
  color: #999;
  margin-bottom: 4px;
}

.meta-item {
  margin-right: 12px;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.tag {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
  background: #f0f0f0;
}

.status-tag.archived {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
  background: #fef0f0;
  color: #f56c6c;
}

.status-tag.locked {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
  background: #fef0f0;
  color: #f56c6c;
}

.status-tag.requested {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
  background: #f0f9eb;
  color: #67c23a;
}

.permission-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 10px;
  color: #fff;
  font-weight: bold;
}

.permission-badge.locked {
  background: #f56c6c;
}

.permission-badge.requested {
  background: #67c23a;
}

.book-cover {
  position: relative;
}

/* 权限申请审核弹窗样式 */
.permission-requests-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.permission-request-item {
  padding: 16px;
  border: 1px solid #f0f0f0;
  border-radius: 6px;
  background: #f9fafc;
}

.request-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.request-user {
  font-weight: 500;
}

.request-status {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.request-status.pending {
  background: #ecf5ff;
  color: #409eff;
}

.request-status.approved {
  background: #f0f9eb;
  color: #67c23a;
}

.request-status.rejected {
  background: #fef0f0;
  color: #f56c6c;
}

.request-content {
  margin-bottom: 12px;
}

.request-reason {
  margin: 0 0 8px 0;
  font-size: 14px;
  line-height: 1.4;
}

.request-meta {
  font-size: 12px;
  color: #999;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.request-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.review-comment {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed #f0f0f0;
  font-size: 13px;
  color: #666;
}

/* 用户权限管理样式 */
.user-permissions-list {
  max-height: 400px;
  overflow-y: auto;
}

.table {
  width: 100%;
  border-collapse: collapse;
  margin: 0;
}

.table th,
.table td {
  padding: 10px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.table th {
  background-color: #f9fafc;
  font-weight: 600;
  font-size: 14px;
}

.table tr:hover {
  background-color: #f9fafc;
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-open {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.status-locked {
  background-color: #ffebee;
  color: #c62828;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-sm:hover {
  opacity: 0.8;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
  color: #999;
}

.loading {
  text-align: center;
  padding: 40px 0;
  color: #666;
}

.spinner {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #409eff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-tip {
  font-size: 13px;
  color: #999;
  margin: 8px 0;
}

.empty-tip.small {
  font-size: 12px;
}

.book-summary {
  padding: 10px 12px;
  border-radius: 6px;
  background: #f7f9fc;
  margin-bottom: 12px;
}

.versions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 14px;
}

.version-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.version-item {
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.version-main {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 2px;
}

.version-tag {
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
  background: #ecf5ff;
  color: #409eff;
}

.version-title {
  font-size: 14px;
}

.version-meta {
  font-size: 11px;
  color: #999;
  display: flex;
  gap: 8px;
}

.version-comment {
  margin: 2px 0 0 0;
  font-size: 12px;
  color: #666;
}

.btn {
  padding: 6px 12px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
  background: #fff;
  font-size: 13px;
  cursor: pointer;
}

.btn-primary {
  background: #409eff;
  border-color: #409eff;
  color: #fff;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

.btn-secondary {
  background: #f5f7fa;
}

.btn-danger {
  background: #f56c6c;
  border-color: #f56c6c;
  color: #fff;
}

.btn-danger:hover {
  background: #f78989;
}

.book-actions {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: flex-start;
  gap: 8px;
}

/* 简单弹窗骨架 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: #fff;
  border-radius: 8px;
  width: 480px;
  max-width: 90%;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.modal-header,
.modal-footer {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
}

.modal-footer {
  border-top: 1px solid #f0f0f0;
  border-bottom: none;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.modal-body {
  padding: 16px;
  font-size: 14px;
}

.close-btn {
  border: none;
  background: none;
  font-size: 20px;
  cursor: pointer;
}

/* 删除弹窗样式 */
.delete-warning {
  font-size: 14px;
  margin-bottom: 8px;
  color: #333;
}

.delete-book-title {
  font-weight: bold;
  color: #f56c6c;
}

.delete-info {
  font-size: 13px;
  color: #999;
}

/* 分页样式 */
.pagination {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.pagination-info {
  font-size: 13px;
  color: #666;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination-btn {
  padding: 4px 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background: #fff;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-btn:hover:not(:disabled) {
  border-color: #409eff;
  color: #409eff;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-page {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-page:hover {
  background: #f5f7fa;
}

.pagination-page.active {
  background: #409eff;
  color: #fff;
}

@media (max-width: 960px) {
  .layout {
    grid-template-columns: 1fr;
  }

  .pagination-controls {
    flex-wrap: wrap;
    justify-content: center;
  }
}

/* 加锁相关样式 */
.lock-tips {
  margin-top: 12px;
  padding: 10px;
  background: #f0f9eb;
  border-radius: 4px;
}

.tip-text {
  margin: 0;
  font-size: 13px;
  color: #67c23a;
}

.lock-logs-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.lock-log-item {
  padding: 12px;
  border: 1px solid #f0f0f0;
  border-radius: 6px;
  background: #f9fafc;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.log-action {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
}

.log-action.lock {
  background: #fef0f0;
  color: #f56c6c;
}

.log-action.unlock,
.log-action.approve_unlock {
  background: #f0f9eb;
  color: #67c23a;
}

.log-action.request_unlock {
  background: #ecf5ff;
  color: #409eff;
}

.log-action.reject_unlock {
  background: #fef0f0;
  color: #f56c6c;
}

.log-time {
  font-size: 12px;
  color: #999;
}

.log-content {
  font-size: 13px;
  color: #666;
}

.log-content p {
  margin: 4px 0;
}
</style>


