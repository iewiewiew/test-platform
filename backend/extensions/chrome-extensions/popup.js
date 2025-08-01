// 测试数据生成器

// 中国省份代码
const PROVINCE_CODES = [
  '11', '12', '13', '14', '15', '21', '22', '23', '31', '32',
  '33', '34', '35', '36', '37', '41', '42', '43', '44', '45',
  '46', '50', '51', '52', '53', '54', '61', '62', '63', '64', '65'
];

// 手机号前缀
const PHONE_PREFIXES = ['130', '131', '132', '133', '134', '135', '136', '137', '138', '139',
  '150', '151', '152', '153', '155', '156', '157', '158', '159',
  '180', '181', '182', '183', '184', '185', '186', '187', '188', '189'];

// 常见姓氏
const SURNAMES = ['王', '李', '张', '刘', '陈', '杨', '赵', '黄', '周', '吴',
  '徐', '孙', '胡', '朱', '高', '林', '何', '郭', '马', '罗',
  '梁', '宋', '郑', '谢', '韩', '唐', '冯', '于', '董', '萧'];

// 常见名字
const GIVEN_NAMES = ['伟', '芳', '娜', '秀英', '敏', '静', '丽', '强', '磊', '军',
  '洋', '勇', '艳', '杰', '娟', '涛', '明', '超', '秀兰', '霞',
  '平', '刚', '桂英', '建华', '文', '华', '红', '建国', '建军', '志强'];

// 地址前缀
const ADDRESS_PREFIXES = ['北京市', '上海市', '广州市', '深圳市', '杭州市', '成都市', '武汉市', '西安市', '南京市', '重庆市'];
const ADDRESS_STREETS = ['中山路', '解放路', '人民路', '建设路', '和平路', '胜利路', '光明路', '新华路', '文化路', '科技路'];
const ADDRESS_NUMBERS = ['1号', '2号', '3号', '5号', '10号', '15号', '20号', '25号', '30号', '50号'];

// 邮箱域名
const EMAIL_DOMAINS = ['gmail.com', 'qq.com', '163.com', '126.com', 'sina.com', 'hotmail.com', 'outlook.com', 'foxmail.com', 'yahoo.com', 'sohu.com'];

// 工具函数：生成随机数字
function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

// 工具函数：生成随机字符串
function randomString(length, charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789') {
  let result = '';
  for (let i = 0; i < length; i++) {
    result += charset.charAt(Math.floor(Math.random() * charset.length));
  }
  return result;
}

// 计算身份证校验码
function calculateIdCardChecksum(idCard17) {
  const weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2];
  const checkCodes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2'];
  
  let sum = 0;
  for (let i = 0; i < 17; i++) {
    sum += parseInt(idCard17[i]) * weights[i];
  }
  return checkCodes[sum % 11];
}

// 生成身份证号
function generateIdCard() {
  // 省份代码（2位）
  const province = PROVINCE_CODES[randomInt(0, PROVINCE_CODES.length - 1)];
  
  // 城市代码（2位）
  const city = String(randomInt(1, 99)).padStart(2, '0');
  
  // 区县代码（2位）
  const district = String(randomInt(1, 99)).padStart(2, '0');
  
  // 出生日期（8位）
  const year = randomInt(1970, 2000);
  const month = String(randomInt(1, 12)).padStart(2, '0');
  const day = String(randomInt(1, 28)).padStart(2, '0');
  const birthDate = `${year}${month}${day}`;
  
  // 顺序码（3位）
  const sequence = String(randomInt(1, 999)).padStart(3, '0');
  
  // 前17位
  const idCard17 = `${province}${city}${district}${birthDate}${sequence}`;
  
  // 校验码（1位）
  const checksum = calculateIdCardChecksum(idCard17);
  
  return idCard17 + checksum;
}

// 生成手机号
function generatePhone() {
  const prefix = PHONE_PREFIXES[randomInt(0, PHONE_PREFIXES.length - 1)];
  const suffix = String(randomInt(10000000, 99999999));
  return `${prefix}${suffix}`;
}

// 生成邮箱
function generateEmail() {
  const username = randomString(randomInt(5, 12), 'abcdefghijklmnopqrstuvwxyz0123456789');
  const domain = EMAIL_DOMAINS[randomInt(0, EMAIL_DOMAINS.length - 1)];
  return `${username}@${domain}`;
}

// 生成中文姓名
function generateName() {
  const surname = SURNAMES[randomInt(0, SURNAMES.length - 1)];
  const givenNameLength = randomInt(1, 2);
  let givenName = '';
  for (let i = 0; i < givenNameLength; i++) {
    givenName += GIVEN_NAMES[randomInt(0, GIVEN_NAMES.length - 1)];
  }
  return surname + givenName;
}

// 生成银行卡号（使用Luhn算法）
function generateBankCard() {
  // 常见银行卡前缀
  const prefixes = ['622202', '622848', '622700', '621700', '622150', '622155', '622156', '622157', '622158', '622159'];
  const prefix = prefixes[randomInt(0, prefixes.length - 1)];
  
  // 生成中间数字
  let cardNumber = prefix;
  for (let i = 0; i < 15 - prefix.length; i++) {
    cardNumber += randomInt(0, 9);
  }
  
  // 计算Luhn校验码
  let sum = 0;
  let isEven = false;
  for (let i = cardNumber.length - 1; i >= 0; i--) {
    let digit = parseInt(cardNumber[i]);
    if (isEven) {
      digit *= 2;
      if (digit > 9) {
        digit -= 9;
      }
    }
    sum += digit;
    isEven = !isEven;
  }
  
  const checksum = (10 - (sum % 10)) % 10;
  return cardNumber + checksum;
}

// 生成地址
function generateAddress() {
  const prefix = ADDRESS_PREFIXES[randomInt(0, ADDRESS_PREFIXES.length - 1)];
  const street = ADDRESS_STREETS[randomInt(0, ADDRESS_STREETS.length - 1)];
  const number = ADDRESS_NUMBERS[randomInt(0, ADDRESS_NUMBERS.length - 1)];
  return `${prefix}${street}${number}`;
}

// 生成UUID
function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

// 生成日期时间
function generateDateTime() {
  const year = randomInt(2020, 2024);
  const month = String(randomInt(1, 12)).padStart(2, '0');
  const day = String(randomInt(1, 28)).padStart(2, '0');
  const hour = String(randomInt(0, 23)).padStart(2, '0');
  const minute = String(randomInt(0, 59)).padStart(2, '0');
  const second = String(randomInt(0, 59)).padStart(2, '0');
  return `${year}-${month}-${day} ${hour}:${minute}:${second}`;
}

// 生成随机字符串
function generateRandomString() {
  const length = randomInt(8, 16);
  return randomString(length);
}

// 数据生成器映射
const generators = {
  idCard: generateIdCard,
  phone: generatePhone,
  email: generateEmail,
  name: generateName,
  bankCard: generateBankCard,
  address: generateAddress,
  uuid: generateUUID,
  datetime: generateDateTime,
  randomString: generateRandomString
};

// 复制到剪贴板
async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    // 降级方案
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    document.body.appendChild(textArea);
    textArea.select();
    try {
      document.execCommand('copy');
      document.body.removeChild(textArea);
      return true;
    } catch (err) {
      document.body.removeChild(textArea);
      return false;
    }
  }
}

// 显示提示消息
function showToast(message) {
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.textContent = message;
  document.body.appendChild(toast);
  
  setTimeout(() => {
    toast.classList.add('show');
  }, 10);
  
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => {
      document.body.removeChild(toast);
    }, 300);
  }, 2000);
}

// 初始化
document.addEventListener('DOMContentLoaded', function() {
  // 绑定生成按钮事件
  document.querySelectorAll('.btn-generate').forEach(button => {
    button.addEventListener('click', function() {
      const type = this.getAttribute('data-type');
      const input = document.getElementById(type);
      if (generators[type]) {
        input.value = generators[type]();
      }
    });
  });

  // 绑定复制按钮事件
  document.querySelectorAll('.btn-copy').forEach(button => {
    button.addEventListener('click', async function() {
      const targetId = this.getAttribute('data-target');
      const input = document.getElementById(targetId);
      if (input && input.value) {
        const success = await copyToClipboard(input.value);
        if (success) {
          showToast('已复制到剪贴板');
        } else {
          showToast('复制失败');
        }
      }
    });
  });

  // 一键生成全部
  document.querySelector('.btn-generate-all').addEventListener('click', function() {
    Object.keys(generators).forEach(type => {
      const input = document.getElementById(type);
      if (input && generators[type]) {
        input.value = generators[type]();
      }
    });
    showToast('已生成全部数据');
  });

  // 点击输入框自动选中文本
  document.querySelectorAll('input[readonly]').forEach(input => {
    input.addEventListener('click', function() {
      this.select();
    });
  });
});






