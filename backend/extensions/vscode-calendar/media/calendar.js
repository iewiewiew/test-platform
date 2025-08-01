(function () {
  const vscode = acquireVsCodeApi();

  let currentDate = new Date();
  let currentYear = currentDate.getFullYear();
  let currentMonth = currentDate.getMonth();

  // 初始化日历
  function initCalendar() {
    renderCalendar();
    setupEventListeners();
  }

  // 渲染日历
  function renderCalendar() {
    const monthYearElement = document.getElementById("monthYear");
    const calendarDaysElement = document.getElementById("calendarDays");

    // 设置月份年份标题
    const monthNames = ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"];
    monthYearElement.textContent = `${currentYear}年 ${monthNames[currentMonth]}`;

    // 清空日历
    calendarDaysElement.innerHTML = "";

    // 获取当月第一天和最后一天
    const firstDay = new Date(currentYear, currentMonth, 1);
    const lastDay = new Date(currentYear, currentMonth + 1, 0);
    const firstDayOfWeek = firstDay.getDay(); // 0-6 (0是周日)
    const daysInMonth = lastDay.getDate();

    // 获取上个月的最后几天
    const prevMonthLastDay = new Date(currentYear, currentMonth, 0).getDate();

    // 填充上个月的日期
    for (let i = firstDayOfWeek - 1; i >= 0; i--) {
      const day = prevMonthLastDay - i;
      const dayElement = createDayElement(day, true);
      calendarDaysElement.appendChild(dayElement);
    }

    // 填充当月的日期
    const today = new Date();
    for (let day = 1; day <= daysInMonth; day++) {
      const isToday = currentYear === today.getFullYear() && currentMonth === today.getMonth() && day === today.getDate();
      const dayElement = createDayElement(day, false, isToday);
      calendarDaysElement.appendChild(dayElement);
    }

    // 填充下个月的日期（填满6行）
    const totalCells = calendarDaysElement.children.length;
    const remainingCells = 42 - totalCells; // 6行 x 7列 = 42
    for (let day = 1; day <= remainingCells; day++) {
      const dayElement = createDayElement(day, true);
      calendarDaysElement.appendChild(dayElement);
    }
  }

  // 创建日期元素
  function createDayElement(day, isOtherMonth, isToday = false) {
    const dayElement = document.createElement("div");
    dayElement.className = "day";
    dayElement.textContent = day;

    if (isOtherMonth) {
      dayElement.classList.add("other-month");
    }

    if (isToday) {
      dayElement.classList.add("today");
    }

    // 创建工具提示
    const tooltip = document.createElement("div");
    tooltip.className = "day-tooltip";

    if (!isOtherMonth) {
      const dateStr = `${currentYear}-${String(currentMonth + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
      tooltip.textContent = dateStr;
      dayElement.appendChild(tooltip);

      // 鼠标悬停事件
      dayElement.addEventListener("mouseenter", function () {
        const date = new Date(currentYear, currentMonth, day);
        const dateInfo = formatDateInfo(date);
        tooltip.textContent = dateInfo;

        // 发送消息到扩展
        vscode.postMessage({
          command: "dateHover",
          date: dateStr,
          dateInfo: dateInfo,
        });
      });
    }

    return dayElement;
  }

  // 格式化日期信息
  function formatDateInfo(date) {
    const weekdays = ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"];
    const year = date.getFullYear();
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const weekday = weekdays[date.getDay()];

    return `${year}年${month}月${day}日 ${weekday}`;
  }

  // 设置事件监听器
  function setupEventListeners() {
    const prevBtn = document.getElementById("prevMonth");
    const nextBtn = document.getElementById("nextMonth");

    prevBtn.addEventListener("click", () => {
      currentMonth--;
      if (currentMonth < 0) {
        currentMonth = 11;
        currentYear--;
      }
      renderCalendar();
    });

    nextBtn.addEventListener("click", () => {
      currentMonth++;
      if (currentMonth > 11) {
        currentMonth = 0;
        currentYear++;
      }
      renderCalendar();
    });
  }

  // 页面加载完成后初始化
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initCalendar);
  } else {
    initCalendar();
  }
})();
