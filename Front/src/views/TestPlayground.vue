<script setup>
import { ref, onMounted } from "vue";
import { api } from "@/api";

const message = ref("");
const healthStatus = ref("");
const inputText = ref("");
const echoResponse = ref("");

const fetchData = async () => {
  try {
    const rootResponse = await api.get("/");
    message.value = rootResponse.data.message;

    const healthResponse = await api.get("/health");
    healthStatus.value = healthResponse.data.status;
  } catch (error) {
    console.error("Error fetching data:", error);
    message.value = "Error connecting to backend";
  }
};

const sendEcho = async () => {
  try {
    const response = await api.post("/echo", {
      message: inputText.value,
    });
    echoResponse.value = response.data.echo;
  } catch (error) {
    console.error("Error sending echo:", error);
    echoResponse.value = "Error sending data";
  }
};

const dbInput = ref("");
const dbItems = ref([]); // 빈 배열로 초기화

const fetchItems = async () => {
  try {
    const response = await api.get("/items");
    // API가 리스트 자체를 반환하므로 response.data.items가 아니라 response.data를 써야 할 수도 있음
    // 하지만 백엔드 응답 모델에 따라 다름. 백엔드가 [{}, {}] 형태라면 response.data가 맞음.
    // 기존 코드: dbItems.value = response.data.items; -> 백엔드가 {"items": []} 형태였음.
    // 방금 수정한 백엔드는 리스트를 바로 반환함: return [ItemResponse(...)]
    // 따라서 response.data로 수정해야 함.
    dbItems.value = response.data; 
  } catch (error) {
    console.error("Error fetching items:", error);
    dbItems.value = []; // 에러 시 빈 배열 유지
  }
};

const saveItem = async () => {
  if (!dbInput.value) return;
  try {
    await api.post("/items", {
      content: dbInput.value,
    });
    dbInput.value = "";
    await fetchItems();
  } catch (error) {
    console.error("Error saving item:", error);
  }
};

onMounted(() => {
  fetchData();
  fetchItems();
});
</script>

<template>
  <div class="flex flex-col items-center gap-12 w-full max-w-[600px] mx-auto pb-20">
    <header>
      <h1 class="border-b border-black pb-4 inline-block transition-colors duration-300 hover:text-luxury-gold">
        QA Automation Workspace
      </h1>
    </header>
    
    <div class="flex justify-center items-center gap-8 border border-black py-6 px-12 w-full bg-white/80 backdrop-blur transition-all duration-500 hover:border-gray-600 hover:shadow-lg hover:-translate-y-0.5 group">
      <div class="flex flex-col items-center gap-2 relative group/item">
        <span class="text-xs uppercase tracking-widest text-gray-500 transition-colors duration-300 group-hover/item:text-luxury-gold">Backend Message</span>
        <span class="font-mono text-lg transition-transform duration-300 group-hover/item:scale-110">{{ message || 'Loading...' }}</span>
      </div>
      
      <div class="w-px h-10 bg-black/30 transition-all duration-300 group-hover:h-12 group-hover:opacity-50"></div>
      
      <div class="flex flex-col items-center gap-2 relative group/item">
        <span class="text-xs uppercase tracking-widest text-gray-500 transition-colors duration-300 group-hover/item:text-luxury-gold">System Health</span>
        <span class="font-mono text-lg transition-transform duration-300 group-hover/item:scale-110" :class="{ 'text-luxury-gold': healthStatus === 'ok' }">{{ healthStatus || 'Checking...' }}</span>
      </div>
    </div>

    <div class="w-full flex flex-col gap-6 group/echo">
      <h2 class="text-base font-normal tracking-[2px] text-luxury-gold m-0 text-left relative w-fit after:content-[''] after:absolute after:bottom-[-5px] after:left-0 after:w-0 after:h-px after:bg-luxury-gold after:transition-all after:duration-500 group-hover/echo:after:w-full">
        ECHO TEST
      </h2>
      
      <div class="flex gap-0">
        <input v-model="inputText" placeholder="Type command..." @keyup.enter="sendEcho" class="flex-1 border-r-0" />
        <button @click="sendEcho">TRANSMIT</button>
      </div>
      
      <div class="border border-black p-6 text-left min-h-[100px] transition-all duration-500 relative overflow-hidden hover:border-gray-400 hover:shadow-inner group/response"
           :class="{ 'border-luxury-gold bg-luxury-gold-light': echoResponse }">
        <span class="block text-[0.7rem] text-gray-400 tracking-widest mb-2 transition-all duration-300 group-hover/response:tracking-[2px] group-hover/response:text-luxury-gold">SERVER RESPONSE</span>
        <p class="m-0 font-mono">{{ echoResponse || 'Waiting for input...' }}</p>
      </div>
    </div>

    <!-- Data Persistence Section -->
    <div class="w-full flex flex-col gap-6 group/db">
      <h2 class="text-base font-normal tracking-[2px] text-luxury-gold m-0 text-left relative w-fit after:content-[''] after:absolute after:bottom-[-5px] after:left-0 after:w-0 after:h-px after:bg-luxury-gold after:transition-all after:duration-500 group-hover/db:after:w-full">
        DATA PERSISTENCE
      </h2>
      
      <div class="flex gap-0">
        <input v-model="dbInput" placeholder="Enter data to save..." @keyup.enter="saveItem" class="flex-1 border-r-0" />
        <button @click="saveItem">SAVE TO DB</button>
      </div>
      
      <div class="flex flex-col gap-2 w-full">
        <div v-if="dbItems.length === 0" class="text-center text-gray-400 py-4 font-mono text-sm border border-dashed border-gray-300">
          No items saved yet
        </div>
        <div v-for="(item, index) in dbItems" :key="index" 
             class="border border-black p-4 text-left hover:border-luxury-gold transition-all duration-300 hover:pl-6 hover:shadow-sm bg-white">
          <span class="font-mono">{{ item }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Scoped styles removed in favor of Tailwind CSS utility classes in the template */
</style>
