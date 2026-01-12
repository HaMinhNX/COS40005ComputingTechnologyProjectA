<template>
  <div class="h-full flex flex-col space-y-5" data-isolated-ui>
    <!-- Vibrant Header - Scaled Down -->
    <div class="relative overflow-hidden bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 p-6 rounded-[1.75rem] shadow-xl shadow-indigo-500/20 text-white">
      <div class="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl -mr-20 -mt-20"></div>
      <div class="absolute bottom-0 left-0 w-48 h-48 bg-white/5 rounded-full blur-2xl -ml-10 -mb-10"></div>
      
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-5 relative z-10">
        <div>
          <h2 class="text-2xl font-black tracking-tight mb-2">Thư Viện Bài Tập</h2>
          <p class="text-indigo-100 font-medium text-sm flex items-center gap-2">
            <span class="w-2 h-2 bg-white rounded-full animate-pulse shadow-[0_0_8px_rgba(255,255,255,0.8)]"></span>
            Kho tàng kiến thức phục hồi chức năng chuẩn y khoa
          </p>
        </div>
        
        <div class="flex items-center gap-3 w-full md:w-auto">
          <!-- View Mode Toggle -->
          <div class="flex bg-white/20 backdrop-blur-md rounded-xl p-0.5 border border-white/30">
            <button 
              @click="viewMode = 'exercises'"
              :class="['px-3 py-1.5 rounded-lg text-xs font-bold transition-all', viewMode === 'exercises' ? 'bg-white text-indigo-600 shadow-lg' : 'text-white hover:bg-white/10']"
            >
              Bài tập lẻ
            </button>
            <button 
              @click="viewMode = 'combos'"
              :class="['px-3 py-1.5 rounded-lg text-xs font-bold transition-all', viewMode === 'combos' ? 'bg-white text-indigo-600 shadow-lg' : 'text-white hover:bg-white/10']"
            >
              Combo
            </button>
          </div>

          <div class="relative flex-1 md:w-48 group">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search class="text-white/70 group-focus-within:text-white transition-colors" :size="16" />
            </div>
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="Tìm kiếm..." 
              class="w-full pl-9 pr-3 py-2 bg-white/20 backdrop-blur-md border-2 border-white/30 text-white placeholder-white/70 rounded-xl text-xs focus:ring-2 focus:ring-white/20 focus:border-white/60 outline-none transition-all font-medium shadow-lg"
            />
          </div>
          <button @click="openAddModal" class="px-3 py-2 bg-white text-indigo-600 rounded-xl text-xs font-bold hover:bg-indigo-50 hover:scale-105 transition-all shadow-xl flex items-center gap-1.5 whitespace-nowrap group">
            <Plus :size="16" class="group-hover:rotate-90 transition-transform duration-300" />
            <span class="hidden sm:inline">Thêm Mới</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Categories with Colorful Pills (Only for Exercises) - Sticky to prevent being covered -->
    <div v-if="viewMode === 'exercises'" class="sticky top-0 z-50 bg-gradient-to-b from-[#f8fafc] via-[#f8fafc] to-transparent pb-4 -mx-4 px-4 pt-2">
      <div class="flex gap-2.5 overflow-x-auto pb-3 custom-scrollbar px-1">
        <button 
          v-for="(cat, idx) in categories" 
          :key="cat"
          @click="selectedCategory = cat"
          :class="[
            'px-4 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all border-2 shadow-sm hover:shadow-lg hover:-translate-y-0.5',
            selectedCategory === cat 
              ? getCategoryActiveClass(idx)
              : 'bg-white text-slate-600 border-slate-200 hover:border-slate-300 hover:text-slate-800'
          ]"
        >
          {{ cat }}
        </button>
      </div>
    </div>

    <!-- Vibrant Exercise Grid - More Compact -->
    <div v-if="viewMode === 'exercises'" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-5 pb-6">
      <div 
        v-for="exercise in filteredExercises" 
        :key="exercise.id"
        class="group bg-white rounded-[1.5rem] border border-slate-100 p-5 shadow-lg hover:shadow-2xl hover:shadow-indigo-500/10 hover:-translate-y-2 transition-all duration-300 flex flex-col relative overflow-hidden"
      >
        <!-- Animated Top Gradient Bar -->
        <div :class="['absolute top-0 left-0 w-full h-1.5 transform origin-left transition-transform duration-500', getGradientClass(exercise.category), 'group-hover:scale-x-100 scale-x-0']"></div>
        
        <!-- Icon and Difficulty Badge -->
        <div class="flex items-start justify-between mb-4">
          <div :class="['w-12 h-12 rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 group-hover:rotate-3 transition-all duration-300', getIconBgClass(exercise.category)]">
            <component :is="exercise.icon" :size="24" :class="getIconColorClass(exercise.category)" />
          </div>
          <span :class="['px-2.5 py-1 rounded-lg text-[10px] font-black uppercase tracking-wider border shadow-sm', getDifficultyClass(exercise.difficulty)]">
            {{ exercise.difficulty }}
          </span>
        </div>
        
        <!-- Title and Description -->
        <h3 class="text-base font-black text-slate-900 mb-2 group-hover:text-indigo-600 transition-colors leading-tight">{{ exercise.name }}</h3>
        <p class="text-xs text-slate-500 line-clamp-2 mb-5 flex-1 leading-relaxed font-medium">{{ exercise.description }}</p>
        
        <!-- Metadata Footer -->
        <div class="flex items-center gap-2 pt-4 border-t border-slate-100">
          <div class="flex items-center gap-1.5 text-xs font-bold text-slate-600 px-2 py-1.5 bg-indigo-50 rounded-lg border border-indigo-100">
            <Clock :size="14" class="text-indigo-500" />
            {{ exercise.duration }} phút
          </div>
          <div class="flex items-center gap-1.5 text-xs font-bold text-slate-600 px-2 py-1.5 bg-purple-50 rounded-lg border border-purple-100">
            <Target :size="14" class="text-purple-500" />
            {{ exercise.target }}
          </div>
        </div>

        <!-- Action Button - Always visible with white background, gradient on hover -->
        <button @click="openDetailModal(exercise)" class="mt-4 w-full py-2.5 bg-white border-2 border-slate-200 text-slate-700 rounded-xl text-xs font-bold transition-all shadow-md hover:bg-gradient-to-r hover:from-indigo-600 hover:to-purple-600 hover:text-white hover:border-transparent hover:shadow-xl hover:shadow-indigo-500/30 flex items-center justify-center gap-2 group-hover:scale-[1.02]">
          <span>Xem Chi Tiết</span>
          <ChevronRight :size="16" />
        </button>
      </div>
    </div>

    <!-- Combos Grid - More Compact -->
    <div v-if="viewMode === 'combos'" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-5 pb-6">
      <div 
        v-for="combo in filteredCombos" 
        :key="combo.combo_id"
        class="group bg-white rounded-[1.5rem] border border-slate-100 p-5 shadow-lg hover:shadow-2xl hover:shadow-indigo-500/10 hover:-translate-y-2 transition-all duration-300 flex flex-col relative overflow-hidden"
      >
        <div class="absolute top-0 left-0 w-full h-1.5 bg-gradient-to-r from-amber-500 to-orange-500 transform origin-left transition-transform duration-500 group-hover:scale-x-100 scale-x-0"></div>
        
        <div class="flex items-start justify-between mb-4">
          <div class="w-12 h-12 rounded-xl flex items-center justify-center shadow-lg bg-amber-50 text-amber-600 group-hover:scale-110 group-hover:rotate-3 transition-all duration-300">
             <span class="text-xl">⚡</span>
          </div>
          <span class="px-2.5 py-1 rounded-lg text-[10px] font-black uppercase tracking-wider border shadow-sm bg-slate-50 text-slate-600 border-slate-200">
            {{ combo.items?.length || 0 }} bài tập
          </span>
        </div>
        
        <h3 class="text-base font-black text-slate-900 mb-2 group-hover:text-amber-600 transition-colors leading-tight">{{ combo.name }}</h3>
        <p class="text-xs text-slate-500 line-clamp-2 mb-4 flex-1 leading-relaxed font-medium">{{ combo.description || 'Không có mô tả' }}</p>
        
        <!-- Combo Items Preview -->
        <div class="flex flex-wrap gap-1.5 mb-4">
          <span v-for="(item, idx) in combo.items?.slice(0, 3)" :key="idx" class="px-2 py-0.5 bg-slate-100 rounded-md text-[10px] font-bold text-slate-600">
            {{ item.exercise_type }}
          </span>
          <span v-if="combo.items?.length > 3" class="px-2 py-0.5 bg-slate-100 rounded-md text-[10px] font-bold text-slate-600">
            +{{ combo.items.length - 3 }}
          </span>
        </div>

        <button class="mt-auto w-full py-2.5 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-xl text-xs font-bold opacity-0 group-hover:opacity-100 transition-all shadow-lg shadow-amber-500/20 hover:shadow-xl hover:shadow-amber-500/30 flex items-center justify-center gap-2 transform translate-y-4 group-hover:translate-y-0">
          <span>Xem Chi Tiết</span>
          <ChevronRight :size="16" />
        </button>
      </div>
    </div>

    <!-- Add Exercise Modal - Compact -->
    <div v-if="showAddModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-md flex items-center justify-center z-[100] p-4">
      <div class="bg-white rounded-[1.75rem] p-6 w-full max-w-lg shadow-2xl border border-slate-100 transform scale-100 transition-all relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-emerald-500 to-teal-500"></div>
        
        <div class="flex items-center justify-between mb-5">
          <h3 class="text-xl font-black text-slate-900">Thêm Bài Tập Mới</h3>
          <button @click="showAddModal = false" class="p-2 hover:bg-slate-50 rounded-xl transition-colors text-slate-400 hover:text-slate-900">
            <X :size="20" />
          </button>
        </div>
        
        <div class="space-y-4">
          <div>
            <label class="block text-[10px] font-black text-slate-500 uppercase tracking-wider mb-2">Tên Bài Tập</label>
            <input type="text" class="w-full px-3 py-2.5 bg-slate-50 border-2 border-slate-200 rounded-xl text-xs focus:ring-2 focus:ring-emerald-500/10 focus:border-emerald-500 outline-none transition-all font-bold text-slate-900 placeholder-slate-400" placeholder="VD: Squat tường" />
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-[10px] font-black text-slate-500 uppercase tracking-wider mb-2">Thời Gian (phút)</label>
              <input type="number" class="w-full px-3 py-2.5 bg-slate-50 border-2 border-slate-200 rounded-xl text-xs focus:ring-2 focus:ring-emerald-500/10 focus:border-emerald-500 outline-none transition-all font-bold text-slate-900 placeholder-slate-400" placeholder="15" />
            </div>
            <div>
              <label class="block text-[10px] font-black text-slate-500 uppercase tracking-wider mb-2">Độ Khó</label>
              <select class="w-full px-3 py-2.5 bg-slate-50 border-2 border-slate-200 rounded-xl text-xs focus:ring-2 focus:ring-emerald-500/10 focus:border-emerald-500 outline-none transition-all font-bold text-slate-900">
                <option>Dễ</option>
                <option>Trung bình</option>
                <option>Khó</option>
              </select>
            </div>
          </div>
          
          <div>
            <label class="block text-[10px] font-black text-slate-500 uppercase tracking-wider mb-2">Mô Tả Chi Tiết</label>
            <textarea rows="3" class="w-full px-3 py-2.5 bg-slate-50 border-2 border-slate-200 rounded-xl text-xs focus:ring-2 focus:ring-emerald-500/10 focus:border-emerald-500 outline-none resize-none transition-all font-medium text-slate-900 placeholder-slate-400" placeholder="Mô tả các bước thực hiện bài tập..."></textarea>
          </div>
        </div>

        <div class="flex justify-end gap-3 mt-6">
          <button @click="showAddModal = false" class="px-5 py-2.5 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100 transition-colors">Hủy bỏ</button>
          <button @click="showAddModal = false" class="px-5 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-xl text-xs font-bold hover:from-emerald-700 hover:to-teal-700 shadow-lg shadow-emerald-600/30 transition-all transform hover:-translate-y-1">Tạo Bài Tập</button>
        </div>
      </div>
    </div>

    <!-- Add Combo Modal - Compact -->
    <div v-if="showComboModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-md flex items-center justify-center z-[100] p-4">
      <div class="bg-white rounded-[1.75rem] p-6 w-full max-w-xl shadow-2xl border border-slate-100 transform scale-100 transition-all relative overflow-hidden max-h-[90vh] flex flex-col">
        <div class="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-amber-500 to-orange-500"></div>
        
        <div class="flex items-center justify-between mb-5 flex-shrink-0">
          <h3 class="text-xl font-black text-slate-900">Tạo Combo Mới</h3>
          <button @click="showComboModal = false" class="p-2 hover:bg-slate-50 rounded-xl transition-colors text-slate-400 hover:text-slate-900">
            <X :size="20" />
          </button>
        </div>
        
        <div class="space-y-4 overflow-y-auto custom-scrollbar pr-2 flex-1">
          <div>
            <label class="block text-[10px] font-black text-slate-500 uppercase tracking-wider mb-2">Tên Combo</label>
            <input v-model="comboForm.name" type="text" class="w-full px-3 py-2.5 bg-slate-50 border-2 border-slate-200 rounded-xl text-xs focus:ring-2 focus:ring-amber-500/10 focus:border-amber-500 outline-none transition-all font-bold text-slate-900 placeholder-slate-400" placeholder="VD: Bài tập buổi sáng" />
          </div>

          <div>
            <label class="block text-[10px] font-black text-slate-500 uppercase tracking-wider mb-2">Mô Tả</label>
            <input v-model="comboForm.description" type="text" class="w-full px-3 py-2.5 bg-slate-50 border-2 border-slate-200 rounded-xl text-xs focus:ring-2 focus:ring-amber-500/10 focus:border-amber-500 outline-none transition-all font-medium text-slate-900 placeholder-slate-400" placeholder="Mô tả ngắn gọn..." />
          </div>
          
          <div>
            <div class="flex items-center justify-between mb-3">
               <label class="block text-[10px] font-black text-slate-500 uppercase tracking-wider">Danh sách bài tập</label>
               <button @click="addComboItem" class="text-[10px] font-bold text-amber-600 hover:text-amber-700 flex items-center gap-1">
                 <Plus :size="12" /> Thêm bài
               </button>
            </div>
            
            <div class="space-y-2">
              <div v-for="(item, idx) in comboForm.items" :key="idx" class="flex items-center gap-2 bg-slate-50 p-2 rounded-lg border border-slate-200 group hover:border-amber-200 transition-colors">
                <span class="w-6 h-6 rounded-full bg-white border border-slate-200 flex items-center justify-center text-[10px] font-bold text-slate-600 shadow-sm">{{ idx + 1 }}</span>
                
                <div class="flex-1 flex gap-1.5">
                  <select v-model="item.exercise_type" class="flex-1 px-2 py-1.5 bg-white border border-slate-200 rounded-lg text-xs font-medium outline-none focus:border-amber-500 focus:ring-2 focus:ring-amber-500/10 transition-all">
                    <optgroup label="Thể chất">
                      <option value="Squat">Squat</option>
                      <option value="Bicep Curl">Bicep Curl</option>
                      <option value="Shoulder Flexion">Shoulder Flexion</option>
                      <option value="Knee Raise">Knee Raise</option>
                    </optgroup>
                    <optgroup label="Trí tuệ (Brain Games)">
                      <option value="Memory Game">Memory Game</option>
                      <option value="Reflex Game">Reflex Game</option>
                      <option value="Color Game">Color Game</option>
                      <option value="Word Scramble">Word Scramble</option>
                      <option value="Math Game">Math Game</option>
                    </optgroup>
                  </select>
                </div>

                <div class="w-20 relative">
                  <input v-model="item.target_reps" type="number" class="w-full px-2 py-1.5 bg-white border border-slate-200 rounded-lg text-xs font-medium outline-none focus:border-amber-500 focus:ring-2 focus:ring-amber-500/10 transition-all" placeholder="Reps" />
                  <span class="absolute right-1.5 top-1/2 -translate-y-1/2 text-[9px] font-bold text-slate-400 pointer-events-none">REPS</span>
                </div>

                <button @click="removeComboItem(idx)" class="w-8 h-8 flex items-center justify-center bg-white border border-slate-200 text-slate-400 hover:text-red-500 hover:border-red-200 hover:bg-red-50 rounded-lg transition-all shadow-sm hover:shadow-md hover:scale-105">
                  <Trash2 :size="14" />
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="flex justify-end gap-3 mt-5 pt-3 border-t border-slate-100 flex-shrink-0">
          <button @click="showComboModal = false" class="px-5 py-2.5 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100 transition-colors">Hủy bỏ</button>
          <button @click="saveCombo" class="px-5 py-2.5 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-xl text-xs font-bold hover:from-amber-600 hover:to-orange-600 shadow-lg shadow-amber-500/30 transition-all transform hover:-translate-y-1">Lưu Combo</button>
        </div>
      </div>
    </div>
    <!-- Exercise Detail Modal - Compact & Responsive -->
    <div v-if="showDetailModal && selectedExercise" @click="showDetailModal = false" class="fixed inset-0 bg-slate-900/60 backdrop-blur-md flex items-center justify-center z-[100] p-4">
      <div @click.stop class="bg-white rounded-[2rem] w-full max-w-4xl shadow-2xl border border-slate-100 overflow-hidden max-h-[90vh] flex flex-col">
        <!-- Header with Close Button -->
        <div class="relative bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 p-6 text-white flex-shrink-0">
          <div class="absolute top-0 right-0 w-48 h-48 bg-white/10 rounded-full blur-3xl -mr-20 -mt-20"></div>
          <button @click="showDetailModal = false" class="absolute top-4 right-4 p-2 hover:bg-white/20 rounded-xl transition-colors text-white z-50 hover:scale-110 active:scale-95">
            <X :size="20" />
          </button>
          
          <div class="relative z-10">
            <div class="flex items-center gap-3 mb-3">
              <div class="w-12 h-12 rounded-xl bg-white/20 backdrop-blur-md flex items-center justify-center text-white shadow-xl">
                <component :is="selectedExercise.icon" :size="24" />
              </div>
              <div>
                <h3 class="text-2xl font-black mb-1">{{ selectedExercise.name }}</h3>
                <span class="px-2.5 py-1 bg-white/20 backdrop-blur-md rounded-lg text-[10px] font-bold uppercase tracking-wider">
                  {{ selectedExercise.category }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Content - Scrollable -->
        <div class="p-6 md:p-8 overflow-y-auto custom-scrollbar bg-white flex-1">
          <div class="max-w-3xl mx-auto space-y-6">
            <!-- Stats Row -->
            <div class="grid grid-cols-3 gap-3">
              <div class="p-4 bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl border border-indigo-100">
                <div class="flex items-center gap-1.5 mb-1.5 text-indigo-600">
                  <Clock :size="16" />
                  <span class="text-[10px] font-black uppercase">Thời lượng</span>
                </div>
                <p class="text-xl font-black text-slate-800">{{ selectedExercise.duration }} <span class="text-xs font-medium text-slate-500">phút</span></p>
              </div>
              <div class="p-4 bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl border border-purple-100">
                <div class="flex items-center gap-1.5 mb-1.5 text-purple-600">
                  <Target :size="16" />
                  <span class="text-[10px] font-black uppercase">Tác động</span>
                </div>
                <p class="text-xl font-black text-slate-800">{{ selectedExercise.target }}</p>
              </div>
              <div class="p-4 bg-gradient-to-br from-pink-50 to-rose-50 rounded-xl border border-pink-100">
                <div class="flex items-center gap-1.5 mb-1.5 text-pink-600">
                  <Activity :size="16" />
                  <span class="text-[10px] font-black uppercase">Độ khó</span>
                </div>
                <p class="text-xl font-black text-slate-800">{{ selectedExercise.difficulty }}</p>
              </div>
            </div>

            <!-- Description -->
            <div class="bg-slate-50 rounded-xl p-5 border border-slate-100">
              <h4 class="text-xs font-black text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                <span class="w-1 h-4 bg-gradient-to-b from-indigo-600 to-purple-600 rounded-full"></span>
                Mô tả chi tiết
              </h4>
              <p class="text-sm text-slate-700 leading-relaxed font-medium">{{ selectedExercise.description }}</p>
            </div>

            <!-- Instructions -->
            <div>
              <h4 class="text-xs font-black text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                <span class="w-1 h-4 bg-gradient-to-b from-indigo-600 to-purple-600 rounded-full"></span>
                Hướng dẫn thực hiện
              </h4>
              <ul class="space-y-3">
                <li class="flex gap-3 items-start">
                  <span class="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-600 to-purple-600 text-white flex items-center justify-center text-xs font-black flex-shrink-0 shadow-lg">1</span>
                  <div class="flex-1 pt-0.5">
                    <p class="text-slate-700 font-semibold mb-0.5 text-sm">Chuẩn bị tư thế</p>
                    <p class="text-slate-500 text-xs">Đứng thẳng, hai chân rộng bằng vai, hít thở sâu để chuẩn bị.</p>
                  </div>
                </li>
                <li class="flex gap-3 items-start">
                  <span class="w-7 h-7 rounded-lg bg-gradient-to-br from-purple-600 to-pink-600 text-white flex items-center justify-center text-xs font-black flex-shrink-0 shadow-lg">2</span>
                  <div class="flex-1 pt-0.5">
                    <p class="text-slate-700 font-semibold mb-0.5 text-sm">Thực hiện động tác</p>
                    <p class="text-slate-500 text-xs">Thực hiện động tác chậm rãi, kiểm soát từng bước di chuyển.</p>
                  </div>
                </li>
                <li class="flex gap-3 items-start">
                  <span class="w-7 h-7 rounded-lg bg-gradient-to-br from-pink-600 to-rose-600 text-white flex items-center justify-center text-xs font-black flex-shrink-0 shadow-lg">3</span>
                  <div class="flex-1 pt-0.5">
                    <p class="text-slate-700 font-semibold mb-0.5 text-sm">Lặp lại và nghỉ ngơi</p>
                    <p class="text-slate-500 text-xs">Lặp lại theo số lần quy định, nghỉ ngơi giữa các hiệp.</p>
                  </div>
                </li>
              </ul>
            </div>
            
            <!-- Video Section - Compact -->
            <div>
              <h4 class="text-xs font-black text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                <span class="w-1 h-4 bg-gradient-to-b from-indigo-600 to-purple-600 rounded-full"></span>
                Video Hướng Dẫn
              </h4>
              <div class="aspect-video bg-gradient-to-br from-slate-900 to-slate-800 rounded-xl flex items-center justify-center text-white/70 font-bold shadow-xl border border-slate-700">
                <span class="flex flex-col items-center gap-2">
                  <PlayCircle :size="40" class="text-white/50" />
                  <span class="text-base">Video hướng dẫn sẽ được cập nhật</span>
                  <span class="text-xs text-white/40">Vui lòng quay lại sau</span>
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Search, Plus, Clock, Target, X, Dumbbell, Activity, Footprints, PersonStanding, RotateCw, ChevronRight, Trash2, PlayCircle } from 'lucide-vue-next'

import { API_BASE_URL } from '../config';
const API_BASE = API_BASE_URL;

const searchQuery = ref('')
const selectedCategory = ref('Tất cả')
const showAddModal = ref(false)
const showComboModal = ref(false)
const showDetailModal = ref(false)
const selectedExercise = ref(null)
const viewMode = ref('exercises') // 'exercises' | 'combos'
const combos = ref([])
const doctorId = ref(null)

const comboForm = ref({
  name: '',
  description: '',
  items: [{ exercise_type: 'Squat', target_reps: 10 }]
})

const categories = ['Tất cả', 'Sức mạnh', 'Linh hoạt', 'Cân bằng', 'Tim mạch', 'Phục hồi']

const exercises = ref([
  { id: 1, name: 'Squat tường', icon: Dumbbell, difficulty: 'Trung bình', duration: 15, target: 'Chân', category: 'Sức mạnh', description: 'Đứng lưng dựa vào tường, hai chân rộng bằng vai. Từ từ hạ thấp cho đến khi đầu gối cúng 90 độ. Giữ lưng thẳng và hít thở đều.' },
  { id: 2, name: 'Nâng chân ngồi', icon: PersonStanding, difficulty: 'Dễ', duration: 10, target: 'Bụng', category: 'Sức mạnh', description: 'Ngồi trên ghế và từ từ nâng một chân cho đến khi thẳng. Giữ vài giây rồi hạ xuống. Lặp lại với chân kia.' },
  { id: 3, name: 'Xoay cổ chân', icon: RotateCw, difficulty: 'Dễ', duration: 5, target: 'Cổ chân', category: 'Linh hoạt', description: 'Xoay cổ chân theo chuyển động tròn để cải thiện sự linh hoạt và giảm cứng đờ. Thực hiện 10 lần mỗi chiều.' },
  { id: 4, name: 'Giãn vai', icon: Activity, difficulty: 'Trung bình', duration: 12, target: 'Vai', category: 'Linh hoạt', description: 'Nâng tay về phía trước và lên cao nhất có thể, giữ khuỷu tay thẳng. Cảm nhận sự căng giãn ở vùng vai và lưng trên.' },
  { id: 5, name: 'Luyện đi bộ', icon: Footprints, difficulty: 'Dễ', duration: 20, target: 'Toàn thân', category: 'Tim mạch', description: 'Đi bộ với tốc độ ổn định, tập trung vào tư thế và cân bằng. Sử dụng gậy hoặc xe đẩy nếu cần thiết để đảm bảo an toàn.' },
  { id: 6, name: 'Plank cải tiến', icon: Dumbbell, difficulty: 'Khó', duration: 8, target: 'Core', category: 'Sức mạnh', description: 'Giữ tư thế plank với cẳng tay và ngón chân chạm đất, giữ lưng thẳng. Siết chặt cơ bụng và hít thở đều.' },
])

const filteredExercises = computed(() => {
  return exercises.value.filter(ex => {
    const matchesSearch = ex.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesCategory = selectedCategory.value === 'Tất cả' || ex.category === selectedCategory.value
    return matchesSearch && matchesCategory
  })
})

const filteredCombos = computed(() => {
  return combos.value.filter(c => c.name.toLowerCase().includes(searchQuery.value.toLowerCase()))
})

function openAddModal() {
  if (viewMode.value === 'exercises') {
    showAddModal.value = true
  } else {
    openComboModal()
  }
}

function openComboModal() {
  comboForm.value = { name: '', description: '', items: [{ exercise_type: 'Squat', target_reps: 10 }] };
  showComboModal.value = true;
}

function addComboItem() {
  comboForm.value.items.push({ exercise_type: 'Squat', target_reps: 10 });
}

function removeComboItem(idx) {
  comboForm.value.items.splice(idx, 1);
}

function openDetailModal(exercise) {
  selectedExercise.value = exercise;
  showDetailModal.value = true;
}

async function loadCombos() {
  try {
    const token = localStorage.getItem('token');
    // Get Doctor ID first if not exists
    if (!doctorId.value) {
      const docRes = await fetch(`${API_BASE}/doctor-id`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (docRes.ok) {
        const data = await docRes.json();
        doctorId.value = data.doctor_id;
      }
    }

    if (doctorId.value) {
      const res = await fetch(`${API_BASE}/combos?doctor_id=${doctorId.value}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) combos.value = await res.json();
    }
  } catch (e) { console.error(e); }
}

async function saveCombo() {
  if (!doctorId.value) return;
  try {
    const payload = {
      doctor_id: doctorId.value,
      name: comboForm.value.name,
      description: comboForm.value.description,
      items: comboForm.value.items.map((item, idx) => ({
        ...item,
        sequence_order: idx + 1
      }))
    };
    
    const token = localStorage.getItem('token');
    const res = await fetch(`${API_BASE}/combos`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      await loadCombos();
      showComboModal.value = false;
    }
  } catch (e) { console.error(e); }
}

onMounted(() => {
  loadCombos()
})

function getDifficultyClass(diff) {
  switch(diff) {
    case 'Dễ': return 'bg-emerald-50 text-emerald-600 border-emerald-200'
    case 'Trung bình': return 'bg-amber-50 text-amber-600 border-amber-200'
    case 'Khó': return 'bg-rose-50 text-rose-600 border-rose-200'
    default: return 'bg-slate-50 text-slate-600 border-slate-200'
  }
}

function getCategoryActiveClass(idx) {
  const classes = [
    'bg-gradient-to-r from-indigo-600 to-purple-600 text-white border-indigo-600',
    'bg-gradient-to-r from-emerald-600 to-teal-600 text-white border-emerald-600',
    'bg-gradient-to-r from-amber-600 to-orange-600 text-white border-amber-600',
    'bg-gradient-to-r from-blue-600 to-cyan-600 text-white border-blue-600',
    'bg-gradient-to-r from-rose-600 to-pink-600 text-white border-rose-600',
    'bg-gradient-to-r from-violet-600 to-purple-600 text-white border-violet-600',
  ]
  return classes[idx % classes.length]
}

function getGradientClass(category) {
  switch(category) {
    case 'Sức mạnh': return 'bg-gradient-to-r from-emerald-500 to-teal-500'
    case 'Linh hoạt': return 'bg-gradient-to-r from-amber-500 to-orange-500'
    case 'Cân bằng': return 'bg-gradient-to-r from-blue-500 to-cyan-500'
    case 'Tim mạch': return 'bg-gradient-to-r from-rose-500 to-pink-500'
    case 'Phục hồi': return 'bg-gradient-to-r from-violet-500 to-purple-500'
    default: return 'bg-gradient-to-r from-indigo-500 to-purple-500'
  }
}

function getIconBgClass(category) {
  switch(category) {
    case 'Sức mạnh': return 'bg-gradient-to-br from-emerald-100 to-teal-100'
    case 'Linh hoạt': return 'bg-gradient-to-br from-amber-100 to-orange-100'
    case 'Cân bằng': return 'bg-gradient-to-br from-blue-100 to-cyan-100'
    case 'Tim mạch': return 'bg-gradient-to-br from-rose-100 to-pink-100'
    case 'Phục hồi': return 'bg-gradient-to-br from-violet-100 to-purple-100'
    default: return 'bg-gradient-to-br from-indigo-100 to-purple-100'
  }
}

function getIconColorClass(category) {
  switch(category) {
    case 'Sức mạnh': return 'text-emerald-600'
    case 'Linh hoạt': return 'text-amber-600'
    case 'Cân bằng': return 'text-blue-600'
    case 'Tim mạch': return 'text-rose-600'
    case 'Phục hồi': return 'text-violet-600'
    default: return 'text-indigo-600'
  }
}
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  height: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: #94a3b8;
}
</style>
