# 候选人 ID 诊断指南

**问题**: "无法获取候选人ID，跳过加载应聘记录"  
**位置**: `JobRequirementsManager.vue:509`  
**原因分析**: localStorage 中没有正确保存候选人 ID

---

## 🔍 快速诊断（在浏览器 Console 中执行）

### 第 1 步：检查 localStorage 中的候选人 ID

在浏览器按 `F12` 打开 DevTools，选择 `Console` 标签，粘贴以下代码：

```javascript
// ========== 诊断脚本 ==========
console.log('📋 === 候选人 ID 诊断报告 ===');
console.log('');

// 1. 检查 localStorage 中的 candidateId
const candidateId = localStorage.getItem('candidateId');
console.log('【1】localStorage.candidateId:');
console.log('  值:', candidateId);
console.log('  类型:', typeof candidateId);
console.log('  是否为 null:', candidateId === null);
console.log('  是否为 "null":', candidateId === 'null');
console.log('  有效性:', candidateId && !isNaN(parseInt(candidateId)) ? '✅ 有效' : '❌ 无效');

// 2. 检查 localStorage 中的其他相关字段
console.log('');
console.log('【2】localStorage 中的所有字段:');
for (let i = 0; i < localStorage.length; i++) {
  const key = localStorage.key(i);
  const value = localStorage.getItem(key);
  if (key.toLowerCase().includes('candidate') || key.toLowerCase().includes('id') || key.toLowerCase().includes('user')) {
    console.log(`  ${key}: ${value}`);
  }
}

// 3. 检查当前页面的 URL
console.log('');
console.log('【3】当前页面:');
console.log('  URL:', window.location.href);
console.log('  路径:', window.location.pathname);

// 4. 检查路由中的 ID 参数
console.log('');
console.log('【4】URL 中的 ID 参数:');
const pathParts = window.location.pathname.split('/');
const assessmentIndex = pathParts.indexOf('assessment');
if (assessmentIndex !== -1 && pathParts[assessmentIndex + 1]) {
  console.log('  ✅ 找到:', pathParts[assessmentIndex + 1]);
} else {
  console.log('  ❌ 没有找到 ID 参数');
}

// 5. 总结建议
console.log('');
console.log('【5】诊断结果:');
if (candidateId && !isNaN(parseInt(candidateId))) {
  console.log('  ✅ localStorage 中有有效的 candidateId');
  console.log('  📌 问题可能在其他地方，请检查网络请求');
} else if (!candidateId) {
  console.log('  ❌ localStorage 中没有 candidateId');
  console.log('  💡 解决方案:');
  console.log('     1. 检查是否已登录');
  console.log('     2. 如果已登录，执行: localStorage.setItem("candidateId", "你的ID")');
  console.log('     3. 然后刷新页面: location.reload()');
} else {
  console.log('  ⚠️  localStorage 中的 candidateId 格式不正确');
  console.log('  当前值:', candidateId);
}

console.log('');
console.log('========== 诊断完成 ==========');
```

**预期输出示例**:
```
【1】localStorage.candidateId:
  值: 1
  类型: string
  是否为 null: false
  有效性: ✅ 有效

【2】localStorage 中的所有字段:
  candidateId: 1
  userType: CANDIDATE
  token: eyJ...

【5】诊断结果:
  ✅ localStorage 中有有效的 candidateId
```

---

## 🆘 常见问题和解决方案

### 问题 1: localStorage 中没有 candidateId

**症状**:
```
【1】localStorage.candidateId: 值: null
【5】诊断结果: ❌ localStorage 中没有 candidateId
```

**原因**:
- 登录失败
- 浏览器 Cookie/Storage 被清除
- 登录后没有正确保存 ID

**解决**:

**方式 A: 重新登录**
```javascript
// 清除所有数据
localStorage.clear();
sessionStorage.clear();
// 刷新页面
location.href = '/';
// 重新登录
```

**方式 B: 手动设置 (调试用)** 
```javascript
// 如果你知道你的候选人 ID
localStorage.setItem('candidateId', '5');  // 替换 5 为你的 ID
location.reload();
```

---

### 问题 2: localStorage 中 candidateId 是字符串 'null'

**症状**:
```
【1】候选人ID: 值: "null"
【1】有效性: ❌ 无效
```

**原因**:
登录时错误地设置了 localStorage

**解决**:
```javascript
// 清除错误值
localStorage.removeItem('candidateId');
// 或设置正确值 (如果知道的话)
localStorage.setItem('candidateId', '1');
location.reload();
```

---

### 问题 3: URL 中没有 ID 参数

**症状**:
```
【3】当前页面: URL: http://localhost:5173/assessment
【4】URL 中的 ID 参数: ❌ 没有找到 ID 参数
```

**原因**:
直接访问了 `/assessment` 而不是 `/assessment/1`

**解决**:

**方式 1**: 如果知道 ID，直接访问
```
http://localhost:5173/assessment/5
```

**方式 2**: 通过登录重定向
```javascript
// 确保登录后重定向到正确的 URL
// 后端应该返回候选人 ID，前端应该导航到 /assessment/{id}
location.href = '/assessment/1';
```

---

## 📊 详细诊断脚本（更多信息）

如果需要更详细的诊断，执行以下脚本：

```javascript
console.log('📋 = 完整诊断报告 =');

// 1. 系统信息
console.log('\n【系统信息】');
console.log('  浏览器:', navigator.userAgent.substring(0, 50));
console.log('  当前时间:', new Date().toLocaleString());

// 2. 页面引用信息
console.log('\n【页面信息】');
console.log('  URL:', window.location.href);
console.log('  主机:', window.location.host);
console.log('  协议:', window.location.protocol);

// 3. localStorage 完整内容
console.log('\n【localStorage 完整内容】');
console.table(
  Object.entries(localStorage).reduce((obj, [key, value]) => {
    obj[key] = value.substring ? value.substring(0, 50) : value;
    return obj;
  }, {})
);

// 4. sessionStorage 完整内容
console.log('\n【sessionStorage 完整内容】');
console.table(
  Object.entries(sessionStorage).reduce((obj, [key, value]) => {
    obj[key] = value.substring ? value.substring(0, 50) : value;
    return obj;
  }, {})
);

// 5. Cookies
console.log('\n【Cookies】');
console.log('  ' + (document.cookie || '(空)'));

// 6. 网络状态
console.log('\n【网络状态】');
console.log('  在线:', navigator.onLine ? '✅ 是' : '❌ 否');

console.log('\n= 诊断完成 =');
```

---

## 🔧 快速修复步骤

如果遇到候选人 ID 问题，按以下步骤操作：

### 步骤 1: 识别问题

打开浏览器 Console，运行快速诊断脚本，查看 `【5】诊断结果`

### 步骤 2: 选择对应的解决方案

| 診斷結果 | 问题 | 解决方案 |
|---------|------|--------|
| ❌ localStorage 中没有 candidateId | 登录失败或被清除 | 重新登录 |
| 值是 "null" | 错误的初始化 | 清除并重新登录 |
| ❌ URL 中没有 ID | 直接打开了错误的 URL | 通过登录重定向 |
| ⚠️ 格式不正确 | 数据损坏 | 清除 localStorage 重新开始 |

### 步骤 3: 验证修复

修复后，再次运行诊断脚本，确保 `【5】诊断结果` 显示 ✅

### 步骤 4: 刷新应用

```javascript
// 刷新应用
location.reload();

// 或完全重新加载（清除缓存）
location.reload(true);
```

---

## 📝 自动诊断和修复脚本

这个脚本可以自动诊断并尝试修复问题：

```javascript
// ========== 自动诊断和修复 ==========
(async function autoDiagnoseAndFix() {
  console.log('🔧 开始自动诊断和修复...');
  
  const candidateId = localStorage.getItem('candidateId');
  
  // 诊断
  if (candidateId && !isNaN(parseInt(candidateId))) {
    console.log('✅ candidateId 有效:', candidateId);
    return { status: 'OK', candidateId };
  }
  
  // 尝试从 URL 提取
  const pathParts = window.location.pathname.split('/');
  const assessmentIndex = pathParts.indexOf('assessment');
  if (assessmentIndex !== -1 && pathParts[assessmentIndex + 1]) {
    const urlId = pathParts[assessmentIndex + 1];
    console.log('💾 从 URL 中发现 ID:', urlId);
    localStorage.setItem('candidateId', urlId);
    console.log('✅ 已保存到 localStorage');
    return { status: 'FIXED_FROM_URL', candidateId: urlId };
  }
  
  // 失败
  console.log('❌ 无法修复 - 需要重新登录');
  return { status: 'FAILED', candidateId: null };
})();
```

---

## 📞 进一步调试

如果上面的诊断脚本不能解决问题，可以：

1. 打开 DevTools Network 标签
2. 查看登录 API 的响应，确认返回了候选人 ID
3. 检查后端 `/register` 或 `/login` 接口是否返回了 ID
4. 查看 `AssessmentView.vue` 中的 `candidateId` computed 属性是否被正确计算

---

## 📚 相关文档

- [START_HERE_JOB_FIX.md](./START_HERE_JOB_FIX.md) - 应聘流程修复指南
- [COMPLETE_STARTUP_GUIDE.md](./COMPLETE_STARTUP_GUIDE.md) - 完整启动指南
- [FRONTEND_DEBUG_GUIDE.md](./FRONTEND_DEBUG_GUIDE.md) - 前端调试指南

---

**最后更新**: 2026-03-28  
**诊断工具版本**: v1.0
