function ajax({
  type = 'get',
  url = window.location.href,
  dataType = 'json',
  async = true,
  contentType = 'application/x-www-form-urlencoded',
  success = null,
  error = null,
  complete = null,
  beforeSend = null,
  data = null,
  headers = null
}) {
  // 存储XMLHttpRequest实例
  let xhr = null;

  // 存储请求成功后返回的数据
  let response = null;

  // 在发送请求前，是否取消请求
  let closed = true;

  // 是否使用了GET方式来请求
  let isGet = type === 'get' || type === 'GET' ? true : false;

  // 格式化发送到服务器的数据，转换为key=value&key=value这种格式
  let formatData = ()=> {
    // 如果用户设置了要发送的数据
    if (data) {
      let arr = [];
      for (let key in data) {
        arr.push(encodeURIComponent(key) + '=' + encodeURIComponent(data[key]));
      }
      // 禁止浏览器缓存
      arr.push('time=' + (+new Date()));
      return arr.join('&');
    }
  };
  // 如果请求方式是GET且发送的数据不为空，在ULR后带上参数
    url = `${location.protocol}${url}`;
  if (data) url = isGet ? url + '?' + formatData() : url;

  // 设置额外的HTTP头信息
  let setHeaders = ()=> {
    // 如果用户设置了额外的头信息
    if (headers) {
      for (let key in headers) {
        // 批量设置头信息
        xhr.setRequestHeader(key, headers[key]);
      }
    }
  };

  // 创建XMLHttpRequest实例
  try {
    // 尝试用标准方法创建XMLHttpRequest实例
    xhr = new XMLHttpRequest();
  } catch (e) {
    // 兼容IE6的方法
    xhr = new ActiveXObject('Microsoft.XMLHTTP');
  }

  // 初始化 HTTP请求
  xhr.open(type, url, async);

  // 执行beforeSend回调，并获取返回值
  closed = beforeSend ? beforeSend(xhr) : true;

  // 判断是否手动取消了请求
  if (closed || closed === undefined) {
    // 没有取消请求，发起请求
    isGet ? xhr.send(null) : (xhr.setRequestHeader('content-type', contentType), setHeaders(), xhr.send(formatData()));
  } else {
    // 取消请求
    return;
  }

  // 监听readyState属性
  xhr.onreadystatechange = ()=> {
    if (xhr.readyState === 4) {
      // 执行complete回调
      complete ? complete(xhr, xhr.status) : null;
      // 请求成功，状态>=200 && < 300 表示成功
      if (xhr.status >= 200 && xhr.status < 300) {
        switch (dataType) {
          case 'json':
            try {
              // 使用JSON.parse()序列化字符串
              response = JSON.parse(xhr.responseText);
            } catch (e) {
              // 使用(new Function('return ' + str))()序列化字符串
              response = (new Function('return ' + xhr.responseText))();
            }
            break;
          case 'text':
            response = xhr.responseText;
            break;
          case 'xml':
            response = xhr.responseXML;
            break;
        }
        // 执行success回调
        success ? success(response, xhr.status, xhr) : null;
      // 请求失败
      } else {
        // 执行error回调
        error ? error(xhr.statusText, xhr.status, xhr) : null;
      }
    }
  }
  // 返回XMLHttpRequest实例
  return xhr;
}

document.addEventListener('DOMContentLoaded', ()=> {
    let menu = document.querySelector('.menu');
    
    document.querySelector('.navbar__webRight').addEventListener('click', event=> {
        if (menu.style.display === 'block') {
            menu.style = 'display: none';
        } else {
            menu.style = 'display: block';
        }
    }, false);

    window.addEventListener('scroll', event=> {
        if (menu.style.display === 'block') {
            menu.style = 'display: none';
        }
    }, false);

});
