<template>
  <footer class="w-full border-t border-white/10 bg-white/5 backdrop-blur-md relative z-10">
    <div class="w-full max-w-[1400px] mx-auto px-6 py-6 text-xs text-slate-400 flex justify-between items-center">
      <div class="flex items-center gap-4">
        <span class="tracking-widest uppercase text-sky-400 font-medium">Hadaboni</span>
        <span class="w-px h-3 bg-white/20 hidden md:block"></span>
        <span class="tracking-widest uppercase hidden md:block">Premium Dashboard</span>
      </div>
      <div class="flex items-center gap-4">
        <span class="font-mono text-[10px] tracking-widest uppercase">© {{ new Date().getFullYear() }} All Rights Reserved.</span>
      </div>
    </div>
  </footer>
</template>

<script setup>
</script>

<style scoped>
</style>
