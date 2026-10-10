(() => {
  const form = document.getElementById("exam-form");
  if (!form) return;

  const cards = Array.from(document.querySelectorAll(".question-card"));
  const palette = Array.from(document.querySelectorAll(".palette-btn"));
  const prev = document.getElementById("prev-btn");
  const next = document.getElementById("next-btn");
  const submit = document.getElementById("submit-btn");
  const countLabel = document.getElementById("question-count");
  const timerLabel = document.getElementById("timer");
  const timerBox = document.querySelector(".timer-box");
  const modal = document.getElementById("submit-modal");
  const cancelSubmit = document.getElementById("cancel-submit");
  const confirmSubmit = document.getElementById("confirm-submit");
  const remainingMeta = document.querySelector('meta[name="exam-remaining"]');
  let current = 0;
  let seconds = Number(remainingMeta?.content || 900);
  let submitted = false;

  function render() {
    cards.forEach((card, i) => {
      card.hidden = i !== current;
      card.classList.toggle("active-question", i === current);
    });
    palette.forEach((button, i) => {
      button.classList.toggle("current", i === current);
      const chosen = form.querySelector(`input[name="q${i}"]:checked`);
      button.classList.toggle("answered", Boolean(chosen));
    });
    countLabel.textContent = `Question ${current + 1} of ${cards.length}`;
    prev.disabled = current === 0;
    prev.style.opacity = current === 0 ? ".45" : "1";
    next.hidden = current === cards.length - 1;
    submit.hidden = current !== cards.length - 1;
  }

  function showQuestion(index) {
    current = Math.max(0, Math.min(cards.length - 1, index));
    render();
  }

  function updateTimer() {
    const minutes = Math.floor(seconds / 60);
    const remainder = seconds % 60;
    timerLabel.textContent = `${String(minutes).padStart(2, "0")}:${String(remainder).padStart(2, "0")}`;
    if (seconds <= 60) timerBox.classList.add("urgent");
    if (seconds <= 0 && !submitted) {
      submitted = true;
      form.submit();
      return;
    }
    seconds -= 1;
  }

  prev.addEventListener("click", () => showQuestion(current - 1));
  next.addEventListener("click", () => showQuestion(current + 1));
  palette.forEach((button) => button.addEventListener("click", () => showQuestion(Number(button.dataset.jump))));
  form.addEventListener("change", render);

  form.addEventListener("submit", (event) => {
    if (submitted) return;
    event.preventDefault();
    modal.hidden = false;
  });
  cancelSubmit.addEventListener("click", () => { modal.hidden = true; });
  confirmSubmit.addEventListener("click", () => {
    submitted = true;
    modal.hidden = true;
    form.submit();
  });

  render();
  updateTimer();
  window.setInterval(updateTimer, 1000);
})();
