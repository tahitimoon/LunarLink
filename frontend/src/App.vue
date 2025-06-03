<template>
    <div id="app">
        <router-view />
    </div>
</template>

<script>
export default {
    name: "App"
};
</script>

<style>
/* Element UI Green Theme Overrides */
/* Primary Color */
:root {
  --el-color-primary: #4CAF50;
  --el-color-primary-light-3: #81C784; /* Lighter green for hover/accents */
  --el-color-primary-light-5: #A5D6A7;
  --el-color-primary-light-7: #C8E6C9;
  --el-color-primary-light-8: #E8F5E9;
  --el-color-primary-light-9: #F1F8E9;
  --el-color-primary-dark-2: #388E3C; /* Darker green for active/focus */
}

/* Buttons */
.el-button--primary {
  background-color: var(--el-color-primary) !important;
  border-color: var(--el-color-primary) !important;
  color: #FFFFFF !important;
}
.el-button--primary:hover {
  background-color: var(--el-color-primary-light-3) !important;
  border-color: var(--el-color-primary-light-3) !important;
}
.el-button--primary:focus, .el-button--primary:active {
  background-color: var(--el-color-primary-dark-2) !important;
  border-color: var(--el-color-primary-dark-2) !important;
}

/* Links */
.el-link--primary {
  color: var(--el-color-primary) !important;
}
.el-link--primary:hover {
  color: var(--el-color-primary-light-3) !important;
}

/* Switch */
.el-switch__core:after {
  /* Default state color for the circle if needed */
}
.el-switch.is-checked .el-switch__core {
  background-color: var(--el-color-primary) !important;
  border-color: var(--el-color-primary) !important;
}

/* Pagination */
.el-pagination.is-background .el-pager li:not(.disabled).active {
  background-color: var(--el-color-primary) !important;
  color: #FFFFFF !important;
}
.el-pagination.is-background .el-pager li:not(.disabled):hover {
  color: var(--el-color-primary) !important;
}


/* Tabs */
.el-tabs__item.is-active {
  color: var(--el-color-primary) !important;
}
.el-tabs__active-bar {
  background-color: var(--el-color-primary) !important;
}
.el-tabs__item:hover {
  color: var(--el-color-primary-light-3) !important;
}

/* Input & Textarea Focus */
.el-input__inner:focus, .el-input.is-active .el-input__inner, .el-input.is-focus .el-input__inner {
  border-color: var(--el-color-primary) !important;
}
.el-textarea__inner:focus {
  border-color: var(--el-color-primary) !important;
}

/* Menu - Active Text Color */
.el-menu-item.is-active {
  color: var(--el-color-primary) !important;
}
.el-submenu__title:hover, .el-menu-item:hover {
 color: var(--el-color-primary-light-3) !important;
}


/* Global Styles (Original) */
html,
body {
    height: 100%;
    width: 100%;
    margin: 0;
    overflow: auto;
    padding: 0;
    background: #fff;
}

body {
    color: #333;
    font-family: "PingFang SC", "Helvetica Neue", Helvetica, "Hiragino Sans GB",
        STHeitiSC-Light, "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
}
</style>
