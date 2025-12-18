<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";

const message = ref("");
const healthStatus = ref("");
const inputText = ref("");
const echoResponse = ref("");

const fetchData = async () => {
  try {
    const rootResponse = await axios.get("http://127.0.0.1:8000/");
    message.value = rootResponse.data.message;

    const healthResponse = await axios.get("http://127.0.0.1:8000/health");
    healthStatus.value = healthResponse.data.status;
  } catch (error) {
    console.error("Error fetching data:", error);
    message.value = "Error connecting to backend";
  }
};

const sendEcho = async () => {
  try {
    const response = await axios.post("http://127.0.0.1:8000/echo", {
      message: inputText.value,
    });
    echoResponse.value = response.data.echo;
  } catch (error) {
    console.error("Error sending echo:", error);
    echoResponse.value = "Error sending data";
  }
};

onMounted(() => {
  fetchData();
});
</script>

<template>
  <div class="container">
    <header>
      <h1>QA Automation Workspace</h1>
    </header>

    <div class="status-bar">
      <div class="status-item">
        <span class="label">Backend Message</span>
        <span class="value">{{ message || "Loading..." }}</span>
      </div>
      <div class="separator"></div>
      <div class="status-item">
        <span class="label">System Health</span>
        <span class="value" :class="{ ok: healthStatus === 'ok' }">{{
          healthStatus || "Checking..."
        }}</span>
      </div>
    </div>

    <div class="echo-section">
      <h2>ECHO TEST</h2>
      <div class="input-group">
        <input
          v-model="inputText"
          placeholder="Type command..."
          @keyup.enter="sendEcho"
        />
        <button @click="sendEcho">TRANSMIT</button>
      </div>

      <div class="response-area" :class="{ 'has-content': echoResponse }">
        <span class="label">SERVER RESPONSE</span>
        <p class="response-text">
          {{ echoResponse || "Waiting for input..." }}
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3rem;
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
}

header h1 {
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 1rem;
  display: inline-block;
  transition: color 0.3s ease;
}

header h1:hover {
  color: var(--color-accent);
}

.status-bar {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 2rem;
  border: 1px solid var(--color-border);
  padding: 1.5rem 3rem;
  width: 100%;

  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(5px);
  transition: all 0.4s ease;
}

.status-bar:hover {
  border-color: #666;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.03);
  transform: translateY(-2px);
}

.status-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  position: relative;
}

.status-item .label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #666;
  transition: color 0.3s;
}

.status-item:hover .label {
  color: var(--color-accent);
}

.status-item .value {
  font-family: monospace;
  font-size: 1.1rem;
  transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.status-item:hover .value {
  transform: scale(1.1);
}

.status-item .value.ok {
  color: var(--color-accent);
}

.separator {
  width: 1px;
  height: 40px;
  background-color: var(--color-border);
  opacity: 0.3;
  transition: height 0.3s;
}

.status-bar:hover .separator {
  height: 50px;
  opacity: 0.5;
}

.echo-section {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.echo-section h2 {
  font-size: 1rem;
  font-weight: 400;
  letter-spacing: 2px;
  color: var(--color-accent);
  margin: 0;
  text-align: left;

  position: relative;
  display: inline-block;
  width: fit-content;
}

.echo-section h2::after {
  content: "";
  position: absolute;
  bottom: -5px;
  left: 0;
  width: 0%;
  height: 1px;
  background-color: var(--color-accent);
  transition: width 0.4s ease;
}

.echo-section:hover h2::after {
  width: 100%;
}

.input-group {
  display: flex;
  gap: 0; /* Attached input and button */

  /* Add focus-within effect to the whole group if desired, 
     but currently input/button have their own styles. */
}

input {
  flex: 1;
  border-right: none;
}

button {
  background-color: var(--color-text);
  color: white;
  border: 1px solid var(--color-text);
}

button:hover {
  background-color: var(--color-accent);
  border-color: var(--color-accent);
  color: white;
}

.response-area {
  border: 1px solid var(--color-border);
  padding: 1.5rem;
  text-align: left;
  min-height: 100px;
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
  position: relative;
  overflow: hidden;
}

.response-area:hover {
  border-color: #999;
  box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.02);
}

.response-area.has-content {
  border-color: var(--color-accent);
  background-color: rgba(153, 101, 21, 0.02);
}

.response-area .label {
  display: block;
  font-size: 0.7rem;
  color: #999;
  letter-spacing: 1px;
  margin-bottom: 0.5rem;
  transition: letter-spacing 0.3s;
}

.response-area:hover .label {
  letter-spacing: 2px;
  color: var(--color-accent);
}

.response-text {
  margin: 0;
  font-family: monospace;
}
</style>
