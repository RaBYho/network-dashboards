<template>
  <div class="flex flex-col h-full bg-gray-50">
    <!-- Topbar -->
    <div
      class="flex items-center justify-between px-5 py-3 bg-white border-b border-gray-200"
    >
      <div class="flex items-center gap-2">
        <i class="ti ti-settings text-blue-500 text-base"></i>
        <span class="text-sm font-medium text-gray-800">Paramètres</span>
      </div>
      <div class="flex items-center gap-2">
        <button
          class="text-xs px-3 py-1 rounded border border-gray-200 text-gray-500 hover:bg-gray-50"
          @click="resetForm"
        >
          Annuler
        </button>
        <button
          class="text-xs px-3 py-1 rounded bg-blue-500 text-white hover:bg-blue-600 flex items-center gap-1"
          @click="saveSettings"
        >
          <i class="ti ti-device-floppy text-xs"></i> Sauvegarder
        </button>
      </div>
    </div>

    <div class="flex flex-1 overflow-hidden">
      <!-- Sous-navigation -->
      <div class="w-44 shrink-0 border-r border-gray-200 bg-white py-3">
        <button
          v-for="section in sections"
          :key="section.id"
          class="w-full flex items-center gap-2 px-4 py-2 text-xs transition-colors"
          :class="
            activeSection === section.id
              ? 'bg-gray-50 text-gray-900 font-medium border-r-2 border-blue-500'
              : 'text-gray-500 hover:bg-gray-50 hover:text-gray-700'
          "
          @click="activeSection = section.id"
        >
          <i
            :class="`ti ${section.icon} text-sm`"
            :style="activeSection === section.id ? 'color:#3B82F6' : ''"
          ></i>
          {{ section.label }}
        </button>
      </div>

      <!-- Contenu des sections -->
      <div class="flex-1 overflow-auto p-5">
        <!-- ── Collecte ── -->
        <div
          v-if="activeSection === 'collecte'"
          class="flex flex-col gap-4 max-w-2xl"
        >
          <div class="text-sm font-medium text-gray-700 mb-1">
            Collecte des données
          </div>

          <div
            class="bg-white border border-gray-200 rounded-lg divide-y divide-gray-100"
          >
            <div class="flex items-center justify-between p-4">
              <div>
                <div class="text-sm text-gray-700 font-medium">
                  Intervalle de collecte
                </div>
                <div class="text-xs text-gray-400 mt-0.5">
                  Fréquence de rafraîchissement des métriques réseau
                </div>
              </div>
              <div class="flex flex-col items-end gap-1">
                <div class="flex items-center gap-3">
                  <input
                    type="range"
                    min="1"
                    max="10"
                    step="1"
                    v-model.number="form.interval"
                    class="w-36 accent-blue-500"
                  />
                  <span class="text-sm font-medium text-blue-600 w-8 text-right"
                    >{{ form.interval }}s</span
                  >
                </div>
                <div class="flex justify-between w-36 text-xs text-gray-400">
                  <span>1s</span><span>5s</span><span>10s</span>
                </div>
              </div>
            </div>

            <div class="flex items-center justify-between p-4">
              <div>
                <div class="text-sm text-gray-700 font-medium">
                  Intervalle de ping
                </div>
                <div class="text-xs text-gray-400 mt-0.5">
                  Fréquence des tests de latence vers les cibles
                </div>
              </div>
              <div class="flex items-center gap-3">
                <input
                  type="range"
                  min="1"
                  max="30"
                  step="1"
                  v-model.number="form.pingInterval"
                  class="w-36 accent-blue-500"
                />
                <span class="text-sm font-medium text-blue-600 w-8 text-right"
                  >{{ form.pingInterval }}s</span
                >
              </div>
            </div>

            <div class="flex items-center justify-between p-4">
              <div>
                <div class="text-sm text-gray-700 font-medium">
                  Nombre de pings par test
                </div>
                <div class="text-xs text-gray-400 mt-0.5">
                  Paquets ICMP envoyés à chaque mesure
                </div>
              </div>
              <input
                type="number"
                min="1"
                max="20"
                v-model.number="form.pingCount"
                class="w-20 text-sm text-center px-2 py-1.5 border border-gray-200 rounded bg-gray-50 text-gray-700 focus:outline-none focus:border-blue-300"
              />
            </div>

            <div class="flex items-center justify-between p-4">
              <div>
                <div class="text-sm text-gray-700 font-medium">
                  Collecte active
                </div>
                <div class="text-xs text-gray-400 mt-0.5">
                  Activer ou suspendre la collecte des métriques
                </div>
              </div>
              <button
                class="w-10 h-5 rounded-full transition-colors relative"
                :class="form.collecteActive ? 'bg-blue-500' : 'bg-gray-200'"
                @click="form.collecteActive = !form.collecteActive"
              >
                <span
                  class="absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-all"
                  :class="form.collecteActive ? 'left-5' : 'left-0.5'"
                ></span>
              </button>
            </div>
          </div>
        </div>

        <!-- ── Cibles ping ── -->
        <div
          v-if="activeSection === 'ping'"
          class="flex flex-col gap-4 max-w-2xl"
        >
          <div class="text-sm font-medium text-gray-700 mb-1">
            Cibles de ping
          </div>

          <div class="bg-white border border-gray-200 rounded-lg p-4">
            <div class="flex flex-wrap gap-2 mb-4">
              <div
                v-for="(target, idx) in form.pingTargets"
                :key="idx"
                class="flex items-center gap-1.5 text-xs px-3 py-1 rounded-full bg-gray-100 border border-gray-200 text-gray-700"
              >
                <span class="font-mono">{{ target }}</span>
                <button
                  class="text-gray-400 hover:text-red-500 transition-colors leading-none"
                  @click="removeTarget(idx)"
                >
                  ×
                </button>
              </div>
            </div>
            <div class="flex gap-2">
              <input
                v-model="newTarget"
                type="text"
                placeholder="ex: 8.8.8.8, google.com, gateway..."
                class="flex-1 text-sm px-3 py-1.5 rounded bg-gray-50 text-gray-700 focus:outline-none transition-all"
                :class="
                  targetValid
                    ? 'border border-gray-200 focus:border-blue-300'
                    : 'border-2 border-red-400 focus:border-red-400'
                "
                @keyup.enter="addTarget"
                @input="onTargetInput"
              />
              <button
                class="text-sm px-4 py-1.5 rounded bg-blue-500 text-white hover:bg-blue-600"
                @click="addTarget"
              >
                + Ajouter
              </button>
            </div>
            <transition name="fade">
              <p
                v-if="targetError"
                class="text-xs text-red-500 mt-2 flex items-center gap-1"
              >
                <i class="ti ti-alert-circle text-xs"></i>
                {{ targetError }}
              </p>
            </transition>
          </div>
        </div>

        <!-- ── Seuils d'alerte ── -->
        <div
          v-if="activeSection === 'seuils'"
          class="flex flex-col gap-4 max-w-2xl"
        >
          <div class="text-sm font-medium text-gray-700 mb-1">
            Seuils d'alerte
          </div>

          <div
            class="bg-white border border-gray-200 rounded-lg divide-y divide-gray-100"
          >
            <div class="flex items-center justify-between p-4">
              <div>
                <div class="text-sm text-gray-700 font-medium">
                  Latence maximale
                </div>
                <div class="text-xs text-gray-400 mt-0.5">
                  Déclenche une alerte si le RTT dépasse ce seuil
                </div>
              </div>
              <div class="flex items-center gap-2">
                <input
                  type="number"
                  min="1"
                  max="1000"
                  v-model.number="form.thresholds.latency_ms"
                  class="w-20 text-sm text-center px-2 py-1.5 border border-gray-200 rounded bg-gray-50 text-gray-700 focus:outline-none focus:border-blue-300"
                />
                <span class="text-xs text-gray-400">ms</span>
              </div>
            </div>

            <div class="flex items-center justify-between p-4">
              <div>
                <div class="text-sm text-gray-700 font-medium">
                  Perte de paquets max.
                </div>
                <div class="text-xs text-gray-400 mt-0.5">
                  Déclenche une alerte si la perte dépasse ce seuil
                </div>
              </div>
              <div class="flex items-center gap-2">
                <input
                  type="number"
                  min="0"
                  max="100"
                  v-model.number="form.thresholds.packet_loss_pct"
                  class="w-20 text-sm text-center px-2 py-1.5 border border-gray-200 rounded bg-gray-50 text-gray-700 focus:outline-none focus:border-blue-300"
                />
                <span class="text-xs text-gray-400">%</span>
              </div>
            </div>

            <div class="flex items-center justify-between p-4">
              <div>
                <div class="text-sm text-gray-700 font-medium">
                  Jitter maximal
                </div>
                <div class="text-xs text-gray-400 mt-0.5">
                  Déclenche une alerte si le jitter dépasse ce seuil
                </div>
              </div>
              <div class="flex items-center gap-2">
                <input
                  type="number"
                  min="1"
                  max="500"
                  v-model.number="form.thresholds.jitter_ms"
                  class="w-20 text-sm text-center px-2 py-1.5 border border-gray-200 rounded bg-gray-50 text-gray-700 focus:outline-none focus:border-blue-300"
                />
                <span class="text-xs text-gray-400">ms</span>
              </div>
            </div>

            <div class="flex items-center justify-between p-4">
              <div>
                <div class="text-sm text-gray-700 font-medium">
                  Taux d'erreur max.
                </div>
                <div class="text-xs text-gray-400 mt-0.5">
                  Déclenche une alerte si le taux d'erreur dépasse ce seuil
                </div>
              </div>
              <div class="flex items-center gap-2">
                <input
                  type="number"
                  min="0"
                  max="100"
                  v-model.number="form.thresholds.error_rate_pct"
                  class="w-20 text-sm text-center px-2 py-1.5 border border-gray-200 rounded bg-gray-50 text-gray-700 focus:outline-none focus:border-blue-300"
                />
                <span class="text-xs text-gray-400">%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- ── Interfaces ── -->
        <div
          v-if="activeSection === 'interfaces'"
          class="flex flex-col gap-4 max-w-2xl"
        >
          <div class="text-sm font-medium text-gray-700 mb-1">
            Interfaces surveillées
          </div>

          <div
            class="bg-white border border-gray-200 rounded-lg divide-y divide-gray-100"
          >
            <div
              v-for="iface in store.interfaces"
              :key="iface.name"
              class="flex items-center justify-between p-4"
            >
              <div class="flex items-center gap-3">
                <span
                  class="w-2 h-2 rounded-full"
                  :class="iface.up ? 'bg-green-500' : 'bg-gray-300'"
                ></span>
                <div>
                  <div
                    class="text-sm font-medium text-gray-700 flex items-center gap-2"
                  >
                    <i :class="`ti ${iface.icon} text-sm text-gray-400`"></i>
                    {{ iface.name }}
                  </div>
                  <div class="text-xs text-gray-400 font-mono mt-0.5">
                    {{ iface.up ? "Active" : "Inactive" }}
                    — {{ iface.name.startsWith("w") ? "Wi-Fi" : "Filaire" }}
                  </div>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <span class="text-xs text-gray-400">Surveiller</span>
                <button
                  class="w-10 h-5 rounded-full transition-colors relative"
                  :class="iface.monitored ? 'bg-blue-500' : 'bg-gray-200'"
                  @click="iface.monitored = !iface.monitored"
                >
                  <span
                    class="absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-all"
                    :class="iface.monitored ? 'left-5' : 'left-0.5'"
                  ></span>
                </button>
              </div>
            </div>
          </div>

          <p class="text-xs text-gray-400 flex items-center gap-1">
            <i class="ti ti-info-circle"></i>
            Les interfaces sont détectées automatiquement par le backend.
          </p>
        </div>
        <!-- ── Apparence ── -->
        <div
          v-if="activeSection === 'apparence'"
          class="flex flex-col gap-4 max-w-2xl"
        >
          <div class="text-sm font-medium text-gray-700 mb-1">Apparence</div>

          <div
            class="bg-white border border-gray-200 rounded-lg divide-y divide-gray-100"
          >
            <div class="flex items-center justify-between p-4">
              <div>
                <div class="text-sm text-gray-700 font-medium">Thème</div>
                <div class="text-xs text-gray-400 mt-0.5">
                  Choisir l'apparence de l'interface
                </div>
              </div>
              <div class="flex gap-2">
                <button
                  v-for="t in themes"
                  :key="t.value"
                  class="text-xs px-3 py-1.5 rounded border transition-colors flex items-center gap-1"
                  :class="
                    form.theme === t.value
                      ? 'bg-blue-50 text-blue-700 border-blue-300'
                      : 'border-gray-200 text-gray-500 hover:bg-gray-50'
                  "
                  @click="
                    form.theme = t.value;
                    store.applyTheme(t.value);
                  "
                >
                  <i :class="`ti ${t.icon} text-xs`"></i>
                  {{ t.label }}
                </button>
              </div>
            </div>

            <div class="flex items-center justify-between p-4">
              <div>
                <div class="text-sm text-gray-700 font-medium">
                  Unité de débit
                </div>
                <div class="text-xs text-gray-400 mt-0.5">
                  Afficher le débit en bits ou en octets
                </div>
              </div>
              <select
                v-model="form.unit"
                class="text-sm px-3 py-1.5 border border-gray-200 rounded bg-gray-50 text-gray-700 focus:outline-none focus:border-blue-300"
              >
                <option value="Mbps">Mbps (mégabits)</option>
                <option value="MBps">MBps (mégaoctets)</option>
              </select>
            </div>

            <div class="flex items-center justify-between p-4">
              <div>
                <div class="text-sm text-gray-700 font-medium">Langue</div>
                <div class="text-xs text-gray-400 mt-0.5">
                  Langue de l'interface
                </div>
              </div>
              <select
                v-model="form.lang"
                class="text-sm px-3 py-1.5 border border-gray-200 rounded bg-gray-50 text-gray-700 focus:outline-none focus:border-blue-300"
              >
                <option value="fr">Français</option>
                <option value="en">English</option>
              </select>
            </div>
          </div>
        </div>

        <!-- ── API ── -->
        <div
          v-if="activeSection === 'api'"
          class="flex flex-col gap-4 max-w-2xl"
        >
          <div class="text-sm font-medium text-gray-700 mb-1">
            Connexion API
          </div>

          <div
            class="bg-white border border-gray-200 rounded-lg divide-y divide-gray-100"
          >
            <div class="flex items-center justify-between p-4">
              <div>
                <div class="text-sm text-gray-700 font-medium">
                  URL du backend
                </div>
                <div class="text-xs text-gray-400 mt-0.5">
                  Adresse de l'API FastAPI
                </div>
              </div>
              <input
                v-model="form.apiUrl"
                type="text"
                class="w-60 text-sm px-3 py-1.5 border border-gray-200 rounded bg-gray-50 text-gray-700 font-mono focus:outline-none focus:border-blue-300"
              />
            </div>

            <div class="flex items-center justify-between p-4">
              <div>
                <div class="text-sm text-gray-700 font-medium">
                  Statut de la connexion
                </div>
                <div class="text-xs text-gray-400 mt-0.5">
                  Vérifie la disponibilité du backend
                </div>
              </div>
              <div class="flex items-center gap-3">
                <div
                  class="flex items-center gap-1.5 text-xs"
                  :class="store.connected ? 'text-green-600' : 'text-red-500'"
                >
                  <span
                    class="w-2 h-2 rounded-full"
                    :class="store.connected ? 'bg-green-500' : 'bg-red-500'"
                  ></span>
                  {{ store.connected ? "Connecté" : "Déconnecté" }}
                </div>
                <button
                  class="text-xs px-3 py-1.5 rounded border border-gray-200 text-gray-500 hover:bg-gray-50 flex items-center gap-1"
                  :disabled="testing"
                  @click="testConnection"
                >
                  <i class="ti ti-plug text-xs"></i>
                  {{ testing ? "Test..." : "Tester" }}
                </button>
              </div>
            </div>

            <div class="flex items-center justify-between p-4">
              <div>
                <div class="text-sm text-gray-700 font-medium">
                  Intervalle de reconnexion
                </div>
                <div class="text-xs text-gray-400 mt-0.5">
                  Délai avant nouvelle tentative si déconnecté
                </div>
              </div>
              <div class="flex items-center gap-2">
                <input
                  type="number"
                  min="5"
                  max="60"
                  v-model.number="form.reconnectInterval"
                  class="w-20 text-sm text-center px-2 py-1.5 border border-gray-200 rounded bg-gray-50 text-gray-700 focus:outline-none focus:border-blue-300"
                />
                <span class="text-xs text-gray-400">s</span>
              </div>
            </div>
          </div>

          <!-- Message test -->
          <div
            v-if="testMessage"
            class="text-xs px-4 py-3 rounded-lg border"
            :class="
              testSuccess
                ? 'bg-green-50 border-green-200 text-green-700'
                : 'bg-red-50 border-red-200 text-red-600'
            "
          >
            <i :class="`ti ${testSuccess ? 'ti-check' : 'ti-x'} mr-1`"></i>
            {{ testMessage }}
          </div>
        </div>
      </div>
    </div>
    <!-- Modal de confirmation -->
    <transition name="fade">
      <div
        v-if="showConfirm"
        class="fixed inset-0 bg-black/40 flex items-center justify-center z-50"
      >
        <div class="bg-white rounded-xl shadow-xl p-6 w-80 flex flex-col gap-4">
          <div class="flex items-center gap-3">
            <div
              class="w-10 h-10 rounded-full bg-amber-50 flex items-center justify-center shrink-0"
            >
              <i class="ti ti-alert-triangle text-amber-500 text-lg"></i>
            </div>
            <div>
              <div class="text-sm font-medium text-gray-800">
                Confirmer les modifications
              </div>
              <div class="text-xs text-gray-400 mt-0.5">
                Voulez-vous vraiment appliquer ces paramètres ?
              </div>
            </div>
          </div>
          <div class="flex gap-2 justify-end">
            <button
              class="text-xs px-4 py-2 rounded border border-gray-200 text-gray-500 hover:bg-gray-50"
              @click="showConfirm = false"
            >
              Annuler
            </button>
            <button
              class="text-xs px-4 py-2 rounded bg-blue-500 text-white hover:bg-blue-600"
              @click="confirmSave"
            >
              Confirmer
            </button>
          </div>
        </div>
      </div>
    </transition>
    <!-- Toast sauvegarde -->
    <transition name="fade">
      <div
        v-if="saved"
        class="fixed bottom-5 right-5 bg-gray-800 text-white text-xs px-4 py-2.5 rounded-lg shadow-lg flex items-center gap-2"
      >
        <i class="ti ti-check text-green-400"></i>
        Paramètres sauvegardés
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { useNetworkStore } from "../stores/networkStore";
import axios from "axios";

const store = useNetworkStore();

// ── Sections de navigation ───────────────────────────
const sections = [
  { id: "collecte", label: "Collecte", icon: "ti-refresh" },
  { id: "ping", label: "Cibles ping", icon: "ti-target" },
  { id: "seuils", label: "Seuils d'alerte", icon: "ti-bell" },
  { id: "interfaces", label: "Interfaces", icon: "ti-server" },
  { id: "apparence", label: "Apparence", icon: "ti-palette" },
  { id: "api", label: "API", icon: "ti-link" },
];
const activeSection = ref("collecte");

// ── Thèmes ───────────────────────────────────────────
const themes = [
  { value: "light", label: "Clair", icon: "ti-sun" },
  { value: "dark", label: "Sombre", icon: "ti-moon" },
  { value: "system", label: "Système", icon: "ti-device-desktop" },
];

// ── Formulaire local (copie du store) ────────────────
const form = reactive({
  interval: store.interval,
  pingInterval: 5,
  pingCount: 4,
  collecteActive: true,
  pingTargets: [...store.pingTargets],
  thresholds: { ...store.thresholds },
  theme: "light",
  unit: "Mbps",
  lang: "fr",
  apiUrl: store.apiUrl,
  reconnectInterval: 10,
});

// ── Cibles ping ──────────────────────────────────────
const newTarget = ref("");
const targetError = ref("");
const targetValid = ref(true);

function validateTarget(val) {
  // Adresse IPv4
  const ipv4 = /^(\d{1,3}\.){3}\d{1,3}$/;
  // Nom de domaine
  const domain =
    /^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$/;
  // Nom d'hôte simple (ex: localhost, gateway)
  const hostname = /^[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]?$/;

  if (ipv4.test(val)) {
    // Vérifier que chaque octet est entre 0 et 255
    const octets = val.split(".").map(Number);
    return octets.every((o) => o >= 0 && o <= 255);
  }
  return domain.test(val) || hostname.test(val);
}

function addTarget() {
  const val = newTarget.value.trim();
  if (!val) return;

  if (!validateTarget(val)) {
    targetError.value = "Adresse IP ou nom de domaine invalide.";
    targetValid.value = false;
    return;
  }
  if (form.pingTargets.includes(val)) {
    targetError.value = "Cette cible existe déjà.";
    targetValid.value = false;
    return;
  }

  form.pingTargets.push(val);
  newTarget.value = "";
  targetError.value = "";
  targetValid.value = true;
}

function onTargetInput() {
  // Reset l'erreur dès que l'utilisateur retape
  targetValid.value = true;
  targetError.value = "";
}
function removeTarget(idx) {
  form.pingTargets.splice(idx, 1);
}
// ── Interfaces ───────────────────────────────────────
const newIface = ref("");

function addIface() {
  const val = newIface.value.trim();
  if (!val) return;
  if (store.interfaces.find((i) => i.name === val)) return;
  store.interfaces.push({ name: val, icon: "ti-network", up: true });
  newIface.value = "";
}

// ── Test de connexion API ────────────────────────────
// ── Test de connexion API ────────────────────────────
const testing = ref(false);
const testMessage = ref("");
const testSuccess = ref(false);

async function testConnection() {
  testing.value = true;
  testMessage.value = "";
  try {
    // Utiliser un endpoint sans paramètre obligatoire
    await axios.get(`${form.apiUrl}/api/interfaces`, { timeout: 3000 });
    testSuccess.value = true;
    testMessage.value = `Connexion réussie à ${form.apiUrl}`;
    // Mise à jour immédiate de l'état global
    store.connected = true;
  } catch {
    testSuccess.value = false;
    testMessage.value = `Impossible de joindre ${form.apiUrl} — vérifie que le backend est lancé.`;
    // Optionnel : lancer un fetch pour tenter de rafraîchir l'état global
    store.fetchMetrics();
  } finally {
    testing.value = false;
  }
}

// ── Sauvegarde ───────────────────────────────────────
const saved = ref(false);
const showConfirm = ref(false);

function saveSettings() {
  showConfirm.value = true;
}
function confirmSave() {
  showConfirm.value = false;

  store.apiUrl = form.apiUrl;
  store.thresholds = { ...form.thresholds };
  store.pingTargets = [...form.pingTargets];
  store.setInterval_(form.interval);
  store.applyTheme(form.theme);

  if (!form.collecteActive) store.stopPolling();
  else store.startPolling();

  saved.value = true;
  setTimeout(() => {
    saved.value = false;
  }, 3000);
}
function resetForm() {
  form.interval = store.interval;
  form.pingTargets = [...store.pingTargets];
  form.thresholds = { ...store.thresholds };
  form.apiUrl = store.apiUrl;
  form.collecteActive = true;
  form.pingInterval = 5;
  form.pingCount = 4;
  form.theme = "light";
  form.unit = "Mbps";
  form.lang = "fr";
  form.reconnectInterval = 10;
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition:
    opacity 0.3s,
    transform 0.3s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>
