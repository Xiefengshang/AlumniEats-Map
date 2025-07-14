// 1. 城市坐标数据 (从 pyecharts.datasets.COORDINATES 提取)
// 请确保这里的 URL 是你自己的 Gist Raw URL 或其他可公开访问的 JSON 文件地址
const CHINA_CITY_COORDS_URL = 'https://gist.githubusercontent.com/Xiefengshang/1eaca8df90ae2ce28655eab00bbcfa3e/raw/ed27dde54db16c7c91c2765b7389646da1aec1c2/gistfile1.txt';
let CHINA_CITY_COORDS = {}; // 全局变量，用于缓存坐标数据

// 2. HTML 和 CSS 模板
const CSS_IMPROVED = `
:root {
  --bg-color: #f4f6f8; --container-bg: #ffffff; --card-bg: #ffffff;
  --primary-text: #343a40; --secondary-text: #6c757d; --accent-color: #17a2b8;
  --border-color: #dee2e6; --shadow-color: rgba(0,0,0,0.08);
}
body {
  font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background-color: var(--bg-color); color: var(--primary-text); margin: 0;
  padding: 20px; box-sizing: border-box; display: flex;
  justify-content: center; align-items: center; min-height: 100vh;
}
.main-container {
  width: 100%; max-width: 1600px; margin: 0 auto; padding: 30px;
  background: var(--container-bg); border-radius: 12px;
  box-shadow: 0 4px 20px var(--shadow-color); position: relative;
}
.header { text-align: center; margin-bottom: 30px; position: relative; }
.header h1 { margin: 0; font-size: 32px; font-weight: 600; color: var(--primary-text); }
.header p { margin: 6px 0 0; color: var(--secondary-text); font-size: 18px; font-weight: 300; }
.header-actions {
  position: absolute;
  top: 50%;
  right: 0;
  transform: translateY(-50%);
}
#download-btn {
  padding: 8px 16px;
  font-size: 14px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color .3s;
}
#download-btn:hover { background-color: #218838; }
.grid-wrapper { display: grid; grid-template-columns: 280px 1fr 280px; gap: 30px; align-items: start; }
.info-column { display: flex; flex-direction: column; gap: 15px; max-height: 700px; overflow-y: auto; padding-right: 8px; }
.info-column::-webkit-scrollbar { width: 6px; }
.info-column::-webkit-scrollbar-track { background: transparent; }
.info-column::-webkit-scrollbar-thumb { background: var(--border-color); border-radius: 3px; }
.info-column::-webkit-scrollbar-thumb:hover { background: var(--accent-color); }
.map-wrapper { position: relative; height: 700px; }
#pyecharts-map { width: 100%; height: 100%; }
.svg-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 5; }
.city-block {
  padding: 14px 18px; background: var(--card-bg); border-left: 4px solid var(--accent-color);
  border-radius: 8px; box-shadow: 0 2px 8px var(--shadow-color);
  transition: transform .3s ease, box-shadow .3s ease;
}
.city-block:hover { transform: translateY(-4px); box-shadow: 0 6px 16px var(--shadow-color); }
.city-block h3 {
  margin: 0 0 8px; color: var(--accent-color); font-size: 16px; font-weight: 600;
  border-bottom: 1px solid var(--border-color); padding-bottom: 4px;
}
.city-block p { margin: 4px 0; color: var(--primary-text); font-size: 14px; line-height: 1.4; }
@media (max-width: 1200px) { .grid-wrapper { grid-template-columns: 220px 1fr 220px; } }
@media (max-width: 992px) {
  .grid-wrapper { grid-template-columns: 1fr; }
  .info-column { max-height: 300px; order: 1; }
  .map-wrapper { order: 0; }
  #right-column { display: none; }
}
@media (max-width: 768px) {
  .header { text-align: center; padding-bottom: 50px; }
  .header-actions { position: static; transform: none; margin-top: 15px; }
}
`;

const HTML_TEMPLATE = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>蹭饭图</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/echarts@4.1.0/map/js/china.js"></script>
  <style>${CSS_IMPROVED}</style>
</head>
<body>
  <div class="main-container">
    <div class="header" id="chart-header">{header_content}</div>
    <div class="grid-wrapper">
      <div class="info-column" id="left-column">{left_blocks}</div>
      <div class="map-wrapper"><div id="pyecharts-map"></div></div>
      <div class="info-column" id="right-column">{right_blocks}</div>
    </div>
    <svg class="svg-overlay" id="svg-layer"></svg>
  </div>
  <script>
    const cityGeoCoords = {geo_coords};
    const chartOptions   = {chart_options};
    document.addEventListener('DOMContentLoaded', () => {
      const chartDom = document.getElementById('pyecharts-map');
      if (!chartDom) return;
      const myChart  = echarts.init(chartDom);
      
      chartOptions.tooltip.formatter = params => {
        const d = params.data && params.data.cityData;
        if (!d) return '';
        let html = \`<strong>\${params.name}</strong> (\${d.students.length}人)<br/>\`;
        d.students.forEach(s => html += \`\${s.name} - \${s.university}<br/>\`);
        return html;
      };
      
      myChart.setOption(chartOptions);
      
      const svg   = document.getElementById('svg-layer');
      const wrap  = document.querySelector('.main-container');
      const draw  = () => {
        if (!svg) return;
        svg.innerHTML = '';
        const cRect = wrap.getBoundingClientRect();
        for (let name in cityGeoCoords) {
          const info = cityGeoCoords[name];
          const block= document.getElementById(\`city-\${name.replace(/ /g,'_')}\`);
          if (!block) continue;
          const bRect = block.getBoundingClientRect();
          const start = {
            x: (info.align === 'left' ? bRect.right  : bRect.left)  - cRect.left,
            y: (bRect.top + bRect.height/2) - cRect.top
          };
          const [px, py] = myChart.convertToPixel('geo', info.coord) || [0, 0];
          const mRect = chartDom.getBoundingClientRect();
          const end = { x: mRect.left - cRect.left + px, y: mRect.top - cRect.top + py };
          if (!end.x || !end.y) continue;
          const path = document.createElementNS('http://www.w3.org/2000/svg','path');
          const c1 = { x: start.x + (end.x - start.x)/2, y: start.y };
          const c2 = { x: start.x + (end.x - start.x)/2, y: end.y };
          path.setAttribute('d', \`M\${start.x} \${start.y} C \${c1.x} \${c1.y}, \${c2.x} \${c2.y}, \${end.x} \${end.y}\`);
          path.setAttribute('stroke','#4f5b6e');
          path.setAttribute('stroke-width','1.5');
          path.setAttribute('stroke-dasharray', '5, 5');
          path.setAttribute('fill','none'); 
          path.setAttribute('opacity','0.8');
          svg.appendChild(path);
        }
      };
      myChart.on('finished', draw);
      myChart.on('georoam',   draw);
      new ResizeObserver(() => { myChart.resize(); draw(); }).observe(wrap);
      window.addEventListener('scroll', draw, true);

      // --- 下载按钮的逻辑 ---
      const downloadBtn = document.getElementById('download-btn');
      if (downloadBtn) {
        downloadBtn.addEventListener('click', () => {
          const headerDiv = document.getElementById('chart-header');
          const actionsDiv = document.querySelector('.header-actions');
          if (actionsDiv) {
            actionsDiv.style.display = 'none'; // 隐藏按钮而不是移除
          }

          const htmlContent = document.documentElement.outerHTML;

          if (actionsDiv) {
            actionsDiv.style.display = ''; // 恢复显示
          }

          const blob = new Blob([htmlContent], { type: 'text/html;charset=utf-8' });
          const a = document.createElement('a');
          a.href = URL.createObjectURL(blob);
          a.download = '我的蹭饭图.html';
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          URL.revokeObjectURL(a.href);
        });
      }
    });
  </script>
</body>
</html>`;

// 3. 用户输入表单页面
const INPUT_FORM_HTML = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>蹭饭图生成器</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body { font-family: sans-serif; background-color: #f4f6f8; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 20px; }
    .container { background: #fff; padding: 30px 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); max-width: 800px; width: 100%; }
    h1 { color: #333; text-align: center; }
    p { color: #666; line-height: 1.6; }
    textarea { width: 100%; height: 300px; margin-top: 10px; padding: 10px; border: 1px solid #ccc; border-radius: 6px; font-family: monospace; font-size: 14px; }
    button { display: block; width: 100%; padding: 12px; margin-top: 20px; background-color: #17a2b8; color: white; border: none; border-radius: 6px; font-size: 16px; cursor: pointer; transition: background-color .3s; }
    button:hover { background-color: #138496; }
    .format-guide { background-color: #e9ecef; padding: 15px; border-radius: 6px; margin-top: 20px; }
  </style>
</head>
<body>
  <div class="container">
    <h1>蹭饭图生成器</h1>
    <p>在这里输入你的朋友信息，我们将为你生成一张专属的“蹭饭根据地”地图！</p>
    
    <div class="format-guide">
      <strong>格式说明:</strong>
      <p>每行代表一个朋友，格式为：<code>城市, 学校, 姓名</code>。请使用英文逗号分隔。</p>
      <p>例如：<br>
      北京, 北京大学, 张三<br>
      上海, 复旦大学, 李四
      </p>
    </div>

    <form method="POST">
      <label for="studentsData"><strong>朋友信息列表:</strong></label>
      <textarea id="studentsData" name="studentsData" placeholder="请按照“城市, 学校, 姓名”的格式输入，每行一个朋友...">${
`北京, 清华大学, 王五
上海, 复旦大学, 李四
广州, 中山大学, 赵六
杭州, 浙江大学, 孙七
成都, 四川大学, 周八
武汉, 武汉大学, 吴九
西安, 西安交通大学, 郑十
太原, 太原理工大学, 贺一鸣
太原, 山西大学, 赖子涵`
      }</textarea>
      <button type="submit">生成我的蹭饭图</button>
    </form>
  </div>
</body>
</html>`;


// 4. Worker 核心逻辑
export default {
  async fetch(request, env, ctx) {
    if (Object.keys(CHINA_CITY_COORDS).length === 0) {
        try {
            const response = await fetch(CHINA_CITY_COORDS_URL);
            if (response.ok) {
                CHINA_CITY_COORDS = await response.json();
            } else {
                return new Response("无法加载城市坐标数据", { status: 500 });
            }
        } catch (e) {
            return new Response("获取城市坐标数据时出错", { status: 500 });
        }
    }

    if (request.method === 'POST') {
      return this.handlePostRequest(request);
    }
    return this.handleGetRequest();
  },

  handleGetRequest() {
    return new Response(INPUT_FORM_HTML, {
      headers: { 'Content-Type': 'text/html;charset=UTF-8' },
    });
  },

  async handlePostRequest(request) {
    const formData = await request.formData();
    const studentsDataText = formData.get('studentsData') || '';

    const parsedData = this.parseStudentData(studentsDataText);
    if (parsedData.length === 0) {
        return new Response("输入数据为空或格式不正确，请返回并检查。", { status: 400 });
    }

    const geoData = this.generateCityGeoData(parsedData);
    const chartOptions = this.createChartOptions(parsedData, geoData);
    const leftBlocks = this.buildInfoBlocks(parsedData, geoData, 'left');
    const rightBlocks = this.buildInfoBlocks(parsedData, geoData, 'right');

    const titleOpt = chartOptions.title[0] || {};
    const headerContent = `
      <h1>${titleOpt.text || ''}</h1>
      <p>${titleOpt.subtext || ''}</p>
      <div class="header-actions">
        <button id="download-btn">下载 HTML</button>
      </div>
    `;
    chartOptions.title[0].show = false;

    const finalHtml = HTML_TEMPLATE
      .replace('{header_content}', headerContent)
      .replace('{left_blocks}', leftBlocks)
      .replace('{right_blocks}', rightBlocks)
      .replace('{geo_coords}', JSON.stringify(geoData))
      .replace('{chart_options}', JSON.stringify(chartOptions));

    return new Response(finalHtml, {
      headers: { 'Content-Type': 'text/html;charset=UTF-8' },
    });
  },

  parseStudentData(text) {
    const cityMap = new Map();
    const lines = text.split('\n').filter(line => line.trim() !== '');

    for (const line of lines) {
      const parts = line.split(/[,，]/).map(p => p.trim());
      if (parts.length !== 3) continue;

      const [cityName, university, name] = parts;
      if (!cityName || !university || !name) continue;

      if (!cityMap.has(cityName)) {
        cityMap.set(cityName, {
          city_name: cityName,
          students: [],
        });
      }
      cityMap.get(cityName).students.push({ name, university });
    }
    return Array.from(cityMap.values());
  },

  generateCityGeoData(data, divisionLong = 114.0) {
    const out = {};
    for (const item of data) {
      const name = item.city_name;
      const coord = CHINA_CITY_COORDS[name];
      if (coord) {
        out[name] = {
          coord: coord,
          align: coord[0] <= divisionLong ? 'left' : 'right',
        };
      } else {
        console.warn(`⚠️ 未找到城市[${name}]的坐标`);
      }
    }
    return out;
  },

  buildInfoBlocks(data, geoData, alignSide) {
    let filtered = data.filter(d => geoData[d.city_name]?.align === alignSide);
    
    filtered.sort((a, b) => {
        const coordA = geoData[a.city_name]?.coord[1] || 0;
        const coordB = geoData[b.city_name]?.coord[1] || 0;
        return coordB - coordA;
    });

    return filtered.map(d => {
      const sid = d.city_name.replace(/ /g, '_');
      const studentsHtml = d.students
        .map(s => `<p>${s.name} - ${s.university}</p>`)
        .join('');
      return `<div class="city-block" id="city-${sid}"><h3>${d.city_name} (${d.students.length}人)</h3>${studentsHtml}</div>`;
    }).join('\n');
  },

  createChartOptions(data, geoData) {
    const fullData = data
      .filter(city => geoData[city.city_name])
      .map(city => ({
        name: city.city_name,
        value: [...geoData[city.city_name].coord, city.students.length],
        cityData: city,
      }));

    const studentCounts = fullData.map(d => d.value[2]);
    const minCount = Math.min(...studentCounts, 0);
    const maxCount = Math.max(...studentCounts, 0);

    return {
      title: [{
        text: "可蹭饭根据地分布",
        subtext: "吃遍祖国大好河山🤤",
        show: true,
      }],
      tooltip: {
        trigger: "item",
        backgroundColor: "rgba(255,255,255,0.95)",
        borderWidth: 1,
        borderColor: "#dee2e6",
        textStyle: { color: "#343a40" },
      },
      visualMap: {
        show: true,
        type: "continuous",
        min: minCount,
        max: maxCount,
        range: [minCount, maxCount],
        calculable: true,
        inRange: {
            color: ["#17a2b8", "#38d9a9", "#ff922b", "#f03e3e"],
        },
        posLeft: "5%",
        posBottom: "5%",
        textStyle: { color: "#343a40" },
      },
      geo: {
        map: "china",
        zoom: 1.2,
        roam: true,
        itemStyle: {
          color: "#e9ecef",
          borderColor: "#dee2e6",
        },
        emphasis: {
          itemStyle: { color: "#17a2b8" },
          label: { show: false },
        },
        label: { show: false },
      },
      series: [{
        name: "毕业生去向",
        type: "scatter",
        coordinateSystem: "geo",
        data: fullData,
        symbolSize: 12,
        emphasis: {
            label: { show: false }
        }
      }],
    };
  },
};