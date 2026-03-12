// Базовая логика SPA: auth + CRUD задач.

const state = {
  token: localStorage.getItem("access_token") || "",
  page: 1,
  limit: 10,
  totalPages: 1,
  search: "",
  status: "",
};

const el = {
  authCard: document.getElementById("authCard"),
  profileCard: document.getElementById("profileCard"),
  tasksCard: document.getElementById("tasksCard"),
  email: document.getElementById("email"),
  password: document.getElementById("password"),
  registerBtn: document.getElementById("registerBtn"),
  loginBtn: document.getElementById("loginBtn"),
  logoutBtn: document.getElementById("logoutBtn"),
  profileInfo: document.getElementById("profileInfo"),
  createTaskForm: document.getElementById("createTaskForm"),
  taskTitle: document.getElementById("taskTitle"),
  taskDescription: document.getElementById("taskDescription"),
  taskStatus: document.getElementById("taskStatus"),
  refreshBtn: document.getElementById("refreshBtn"),
  searchInput: document.getElementById("searchInput"),
  statusFilter: document.getElementById("statusFilter"),
  limitFilter: document.getElementById("limitFilter"),
  applyFiltersBtn: document.getElementById("applyFiltersBtn"),
  tasksList: document.getElementById("tasksList"),
  prevPageBtn: document.getElementById("prevPageBtn"),
  nextPageBtn: document.getElementById("nextPageBtn"),
  pageInfo: document.getElementById("pageInfo"),
  toast: document.getElementById("toast"),
};

function toast(message) {
  el.toast.textContent = message;
  el.toast.classList.add("show");
  setTimeout(() => el.toast.classList.remove("show"), 2200);
}

async function request(path, { method = "GET", body = null, auth = false } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth && state.token) headers.Authorization = `Bearer ${state.token}`;

  const response = await fetch(path, {
    method,
    headers,
    body: body ? JSON.stringify(body) : null,
  });

  const text = await response.text();
  const data = text ? JSON.parse(text) : null;

  if (!response.ok) {
    const detail = data?.detail || `Ошибка ${response.status}`;
    throw new Error(detail);
  }

  return data;
}

function updateAuthUI(isAuthed) {
  el.authCard.classList.toggle("hidden", isAuthed);
  el.profileCard.classList.toggle("hidden", !isAuthed);
  el.tasksCard.classList.toggle("hidden", !isAuthed);
}

async function loadProfile() {
  const profile = await request("/auth/me", { auth: true });
  el.profileInfo.textContent = `${profile.email} (id=${profile.id})`;
}

function taskRow(task) {
  const root = document.createElement("article");
  root.className = "task-item";
  root.innerHTML = `
    <h3>${task.title}</h3>
    <div class="task-meta">
      <span>Статус: <b>${task.status}</b></span>
      <span>#${task.id}</span>
    </div>
    <div>${task.description || "Без описания"}</div>
    <div class="task-actions">
      <button class="btn btn-ghost" data-action="next-status">Сменить статус</button>
      <button class="btn btn-danger" data-action="delete">Удалить</button>
    </div>
  `;

  root.querySelector('[data-action="next-status"]').addEventListener("click", async () => {
    try {
      const statuses = ["todo", "in_progress", "done"];
      const next = statuses[(statuses.indexOf(task.status) + 1) % statuses.length];
      await request(`/tasks/${task.id}`, { method: "PATCH", auth: true, body: { status: next } });
      toast("Статус обновлен");
      await loadTasks();
    } catch (error) {
      toast(error.message);
    }
  });

  root.querySelector('[data-action="delete"]').addEventListener("click", async () => {
    try {
      await request(`/tasks/${task.id}`, { method: "DELETE", auth: true });
      toast("Задача удалена");
      await loadTasks();
    } catch (error) {
      toast(error.message);
    }
  });

  return root;
}

async function loadTasks() {
  const params = new URLSearchParams({ page: String(state.page), limit: String(state.limit) });
  if (state.search) params.set("search", state.search);
  if (state.status) params.set("status", state.status);

  const data = await request(`/tasks/?${params.toString()}`, { auth: true });

  state.totalPages = Math.max(data.pages || 1, 1);
  el.pageInfo.textContent = `Страница ${state.page} из ${state.totalPages}`;
  el.prevPageBtn.disabled = state.page <= 1;
  el.nextPageBtn.disabled = state.page >= state.totalPages;

  el.tasksList.innerHTML = "";
  if (!data.items.length) {
    el.tasksList.innerHTML = '<article class="task-item">Задачи не найдены</article>';
    return;
  }

  data.items.forEach((task) => el.tasksList.appendChild(taskRow(task)));
}

async function authRegister() {
  const email = el.email.value.trim();
  const password = el.password.value;
  if (!email || !password) return;

  await request("/auth/register", { method: "POST", body: { email, password } });
  toast("Регистрация выполнена, теперь войдите");
}

async function authLogin() {
  const email = el.email.value.trim();
  const password = el.password.value;
  if (!email || !password) return;

  const tokenData = await request("/auth/login", { method: "POST", body: { email, password } });
  state.token = tokenData.access_token;
  localStorage.setItem("access_token", state.token);
  updateAuthUI(true);
  await loadProfile();
  await loadTasks();
  toast("Вход выполнен");
}

function logout() {
  state.token = "";
  localStorage.removeItem("access_token");
  updateAuthUI(false);
  el.tasksList.innerHTML = "";
  toast("Вы вышли из системы");
}

async function createTask(event) {
  event.preventDefault();
  const title = el.taskTitle.value.trim();
  if (!title) return;

  await request("/tasks/", {
    method: "POST",
    auth: true,
    body: {
      title,
      description: el.taskDescription.value.trim() || null,
      status: el.taskStatus.value,
    },
  });

  el.createTaskForm.reset();
  el.taskStatus.value = "todo";
  toast("Задача создана");
  await loadTasks();
}

function bindEvents() {
  el.registerBtn.addEventListener("click", () => authRegister().catch((e) => toast(e.message)));
  el.loginBtn.addEventListener("click", () => authLogin().catch((e) => toast(e.message)));
  el.logoutBtn.addEventListener("click", logout);
  el.createTaskForm.addEventListener("submit", (e) => createTask(e).catch((err) => toast(err.message)));

  el.refreshBtn.addEventListener("click", () => loadTasks().catch((e) => toast(e.message)));
  el.applyFiltersBtn.addEventListener("click", () => {
    state.search = el.searchInput.value.trim();
    state.status = el.statusFilter.value;
    state.limit = Number(el.limitFilter.value) || 10;
    state.page = 1;
    loadTasks().catch((e) => toast(e.message));
  });

  el.prevPageBtn.addEventListener("click", () => {
    if (state.page > 1) {
      state.page -= 1;
      loadTasks().catch((e) => toast(e.message));
    }
  });

  el.nextPageBtn.addEventListener("click", () => {
    if (state.page < state.totalPages) {
      state.page += 1;
      loadTasks().catch((e) => toast(e.message));
    }
  });
}

async function bootstrap() {
  bindEvents();

  if (!state.token) {
    updateAuthUI(false);
    return;
  }

  try {
    updateAuthUI(true);
    await loadProfile();
    await loadTasks();
  } catch {
    logout();
  }
}

bootstrap();
