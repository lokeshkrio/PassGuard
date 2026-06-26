document.addEventListener('DOMContentLoaded', () => {
  // Theme Toggle Script
  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const isDark = savedTheme === 'dark' || (!savedTheme && systemPrefersDark);

    function setTheme(dark) {
      if (dark) {
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
      } else {
        document.documentElement.removeAttribute('data-theme');
        localStorage.setItem('theme', 'light');
      }
    }

    setTheme(isDark);

    themeToggle.addEventListener('click', () => {
      const currentIsDark = document.documentElement.getAttribute('data-theme') === 'dark';
      setTheme(!currentIsDark);
    });
  }

  // Pipeline step hover highlight script
  document.querySelectorAll('.pipeline-step').forEach(step => {
    step.addEventListener('mouseenter', () => {
      const targetId = step.getAttribute('data-target');
      const targetGroup = document.getElementById(targetId);
      if (targetGroup) targetGroup.classList.add('active-highlight');
    });
    step.addEventListener('mouseleave', () => {
      const targetId = step.getAttribute('data-target');
      const targetGroup = document.getElementById(targetId);
      if (targetGroup) targetGroup.classList.remove('active-highlight');
    });
  });

  // Inject Copy Buttons Dynamically
  document.querySelectorAll('pre').forEach(pre => {
    if (pre.querySelector('code') === null) return;
    if (pre.querySelector('.copy-btn') !== null) return; // Prevent duplicate injection
    
    const btn = document.createElement('button');
    btn.className = 'copy-btn';
    btn.innerText = 'Copy';
    btn.setAttribute('aria-label', 'Copy code to clipboard');

    btn.addEventListener('click', () => {
      const code = pre.querySelector('code').innerText;
      navigator.clipboard.writeText(code).then(() => {
        btn.innerText = 'Copied!';
        setTimeout(() => {
          btn.innerText = 'Copy';
        }, 2000);
      });
    });

    pre.appendChild(btn);
  });

  // Initialize interactive preview if on index page
  if (document.getElementById('preview-pwd')) {
    showPreview('very-weak');
  }
});

// Tab switching
function openTab(evt, tabId) {
  var i, tabcontent, tablinks;
  tabcontent = document.getElementsByClassName("tab-pane");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].classList.remove("active");
  }
  tablinks = document.getElementsByClassName("tab-btn");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].classList.remove("active");
  }
  const targetPane = document.getElementById(tabId);
  if (targetPane) targetPane.classList.add("active");
  if (evt && evt.currentTarget) evt.currentTarget.classList.add("active");
}

// Live Preview Data for Password Categories
const previewData = {
  'very-weak': {
    password: '"123456"',
    score: '5 / 100',
    scoreClass: 'out-bad',
    strength: 'Very Weak',
    strengthClass: 'out-bad',
    theoretical: '19.93 bits',
    effective: '4.32 bits',
    effectiveClass: 'out-bad',
    patterns: "Sequential digits '123456', Keyboard walk '123456'",
    patternsClass: 'out-bad',
    crack: '9.99e-10 seconds (< 0.0001s)',
    crackClass: 'out-bad',
    recs: [
      '[High] Password is too short. Use at least 8 characters, preferably 12 or more.',
      "[High] Avoid using sequences like '123456'.",
      '[High] Avoid using sequential keyboard paths (123456).',
      '[High] Your password is a common word or a simple variation of one. Avoid using common dictionary words.'
    ]
  },
  'weak': {
    password: '"password"',
    score: '47 / 100',
    scoreClass: 'out-warn',
    strength: 'Weak',
    strengthClass: 'out-warn',
    theoretical: '37.60 bits',
    effective: '37.60 bits',
    effectiveClass: 'out-warn',
    patterns: 'None (matched in dictionary)',
    patternsClass: '',
    crack: '10.42 seconds',
    crackClass: 'out-bad',
    recs: [
      '[High] Your password is a common word or a simple variation of one. Avoid using common dictionary words.'
    ]
  },
  'moderate': {
    password: '"MyPass!"',
    score: '55 / 100',
    scoreClass: 'out-warn',
    strength: 'Moderate',
    strengthClass: 'out-warn',
    theoretical: '44.75 bits',
    effective: '44.75 bits',
    effectiveClass: 'out-warn',
    patterns: 'None (matched in dictionary)',
    patternsClass: '',
    crack: '1479.32 seconds (~24.6 mins)',
    crackClass: 'out-warn',
    recs: [
      '[High] Password is too short. Use at least 8 characters, preferably 12 or more.',
      '[Medium] Your password contains common dictionary words. Consider using unrelated words or a passphrase.'
    ]
  },
  'strong': {
    password: '"Password123!"',
    score: '83 / 100',
    scoreClass: 'out-good',
    strength: 'Strong',
    strengthClass: 'out-good',
    theoretical: '78.66 bits',
    effective: '66.55 bits',
    effectiveClass: 'out-good',
    patterns: "Sequential characters '123', Keyboard walk '123'",
    patternsClass: 'out-warn',
    crack: '5.40e+09 seconds (~171.3 years)',
    crackClass: 'out-good',
    recs: [
      '[Low] Avoid using sequences like \'123\'.',
      '[Low] Avoid using sequential keyboard paths (123).',
      '[Medium] Your password contains common dictionary words. Consider using unrelated words or a passphrase.'
    ]
  },
  'very-strong': {
    password: '"c0rr3ct-b4tt3ry-st4pl3-str0ng!"',
    score: '100 / 100',
    scoreClass: 'out-good',
    strength: 'Very Strong',
    strengthClass: 'out-good',
    theoretical: '182.62 bits',
    effective: '182.62 bits',
    effectiveClass: 'out-good',
    patterns: 'None (excellent complexity)',
    patternsClass: 'out-good',
    crack: '4.71e+44 seconds (Centuries)',
    crackClass: 'out-good',
    recs: [
      '✨ None (Excellent password!)'
    ]
  }
};

// Live JSON Representations
const previewJsonData = {
  'very-weak': `{
  "password": "123456",
  "score": 5,
  "strength": "Very Weak",
  "entropy": {
    "theoretical_bits": 19.93,
    "effective_bits": 4.32
  },
  "patterns_detected": [
    {
      "type": "SEQUENTIAL_DIGITS",
      "start": 0,
      "end": 6,
      "description": "Sequential characters '123456' found."
    },
    {
      "type": "KEYBOARD_WALK",
      "start": 0,
      "end": 6,
      "description": "Keyboard walk pattern '123456' found."
    }
  ],
  "crack_times": {
    "online_throttled_seconds": 0.99,
    "online_unthrottled_seconds": 0.01,
    "offline_slow_hash_seconds": 0.001,
    "offline_fast_hash_seconds": 1.0e-9
  },
  "recommendations": [
    "Password is too short. Use at least 8 characters, preferably 12 or more.",
    "Avoid using sequences like '123456'.",
    "Avoid using sequential keyboard paths (123456).",
    "Your password is a common word or a simple variation of one. Avoid using common dictionary words."
  ]
}`,
  'weak': `{
  "password": "password",
  "score": 47,
  "strength": "Weak",
  "entropy": {
    "theoretical_bits": 37.60,
    "effective_bits": 37.60
  },
  "patterns_detected": [],
  "crack_times": {
    "online_throttled_seconds": 1.04e10,
    "online_unthrottled_seconds": 1.04e8,
    "offline_slow_hash_seconds": 1.04e7,
    "offline_fast_hash_seconds": 10.42
  },
  "recommendations": [
    "Your password is a common word or a simple variation of one. Avoid using common dictionary words."
  ]
}`,
  'moderate': `{
  "password": "MyPass!",
  "score": 55,
  "strength": "Moderate",
  "entropy": {
    "theoretical_bits": 44.75,
    "effective_bits": 44.75
  },
  "patterns_detected": [],
  "crack_times": {
    "online_throttled_seconds": 1.48e12,
    "online_unthrottled_seconds": 1.48e10,
    "offline_slow_hash_seconds": 1.48e9,
    "offline_fast_hash_seconds": 1479.32
  },
  "recommendations": [
    "Password is too short. Use at least 8 characters, preferably 12 or more.",
    "Your password contains common dictionary words. Consider using unrelated words or a passphrase."
  ]
}`,
  'strong': `{
  "password": "Password123!",
  "score": 83,
  "strength": "Strong",
  "entropy": {
    "theoretical_bits": 78.66,
    "effective_bits": 66.55
  },
  "patterns_detected": [
    {
      "type": "SEQUENTIAL_DIGITS",
      "start": 8,
      "end": 11,
      "description": "Sequential characters '123' found."
    },
    {
      "type": "KEYBOARD_WALK",
      "start": 8,
      "end": 11,
      "description": "Keyboard walk pattern '123' found."
    }
  ],
  "crack_times": {
    "online_throttled_seconds": 5.40e18,
    "online_unthrottled_seconds": 5.40e16,
    "offline_slow_hash_seconds": 5.40e15,
    "offline_fast_hash_seconds": 5.40e9
  },
  "recommendations": [
    "Avoid using sequences like '123'.",
    "Avoid using sequential keyboard paths (123).",
    "Your password contains common dictionary words. Consider using unrelated words or a passphrase."
  ]
}`,
  'very-strong': `{
  "password": "c0rr3ct-b4tt3ry-st4pl3-str0ng!",
  "score": 100,
  "strength": "Very Strong",
  "entropy": {
    "theoretical_bits": 182.62,
    "effective_bits": 182.62
  },
  "patterns_detected": [],
  "crack_times": {
    "online_throttled_seconds": 4.71e53,
    "online_unthrottled_seconds": 4.71e51,
    "offline_slow_hash_seconds": 4.71e50,
    "offline_fast_hash_seconds": 4.71e44
  },
  "recommendations": []
}`
};

let currentFormat = 'obj';
let currentPreviewKey = 'very-weak';

function setViewFormat(fmt) {
  currentFormat = fmt;
  document.querySelectorAll('.fmt-btn').forEach(btn => btn.classList.remove('active'));
  const btn = document.getElementById(`fmt-${fmt}-btn`);
  if (btn) btn.classList.add('active');

  const objView = document.getElementById('preview-obj-view');
  const jsonView = document.getElementById('preview-json-view');
  const jsonCode = document.getElementById('json-code-block');

  if (fmt === 'obj') {
    if (objView) objView.style.display = 'block';
    if (jsonView) jsonView.style.display = 'none';
  } else {
    if (objView) objView.style.display = 'none';
    if (jsonView) jsonView.style.display = 'block';
    if (jsonCode) jsonCode.innerText = previewJsonData[currentPreviewKey];
  }
}

function showPreview(key) {
  currentPreviewKey = key;
  
  // Update active tab buttons
  document.querySelectorAll('.preview-btn').forEach(btn => {
    btn.classList.remove('active');
  });
  
  // Find button by its onclick function
  const activeBtn = Array.from(document.querySelectorAll('.preview-btn')).find(btn => {
    return btn.getAttribute('onclick') && btn.getAttribute('onclick').includes(key);
  });
  if (activeBtn) activeBtn.classList.add('active');

  const data = previewData[key];
  if (!data) return;

  // Update values
  const pwdEl = document.getElementById('preview-pwd');
  if (pwdEl) pwdEl.innerText = data.password;
  
  const scoreEl = document.getElementById('preview-score');
  if (scoreEl) {
    scoreEl.innerText = data.score;
    scoreEl.className = 'out-v ' + (data.scoreClass || '');
  }

  const strengthEl = document.getElementById('preview-strength');
  if (strengthEl) {
    strengthEl.innerText = data.strength;
    strengthEl.className = 'out-v ' + (data.strengthClass || '');
  }

  const theoreticalEl = document.getElementById('preview-theoretical');
  if (theoreticalEl) theoreticalEl.innerText = data.theoretical;

  const effectiveEl = document.getElementById('preview-effective');
  if (effectiveEl) {
    effectiveEl.innerText = data.effective;
    effectiveEl.className = 'out-v ' + (data.effectiveClass || '');
  }

  const patternsEl = document.getElementById('preview-patterns');
  if (patternsEl) {
    patternsEl.innerText = data.patterns;
    patternsEl.className = 'out-v ' + (data.patternsClass || '');
  }

  const crackEl = document.getElementById('preview-crack');
  if (crackEl) {
    crackEl.innerText = data.crack;
    crackEl.className = 'out-v ' + (data.crackClass || '');
  }

  // Recommendations list
  const recsEl = document.getElementById('preview-recs');
  if (recsEl) {
    recsEl.innerHTML = '';
    data.recs.forEach(rec => {
      const div = document.createElement('div');
      div.style.marginBottom = '4px';
      
      if (rec.includes('[High]')) {
        div.innerHTML = `<span class="out-bad" style="font-weight: 600;">[HIGH]</span> ${rec.replace('[High]', '')}`;
      } else if (rec.includes('[Medium]')) {
        div.innerHTML = `<span class="out-warn" style="font-weight: 600;">[MEDIUM]</span> ${rec.replace('[Medium]', '')}`;
      } else if (rec.includes('[Low]')) {
        div.innerHTML = `<span class="out-good" style="font-weight: 600;">[LOW]</span> ${rec.replace('[Low]', '')}`;
      } else {
        div.innerHTML = rec;
      }
      recsEl.appendChild(div);
    });
  }

  const jsonCode = document.getElementById('json-code-block');
  if (currentFormat === 'json' && jsonCode) {
    jsonCode.innerText = previewJsonData[key];
  }
}
