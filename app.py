import streamlit as st
import yt_dlp
import os
import tempfile
import shutil

st.set_page_config(page_title="亚马逊视频下载器", layout="centered")
st.title("📦 亚马逊视频下载器")
st.caption("适用于公开的产品视频、无 DRM 保护的亚马逊视频链接。付费 / Prime Video 内容通常无法下载。")
st.caption("Created By Harvey")


# 用户输入
url = st.text_input("请输入亚马逊视频页面链接", placeholder="https://www.amazon.com/...")

if url:
    # 临时目录存放下载文件
    tmp_dir = tempfile.mkdtemp()
    
    # yt-dlp 配置
    ydl_opts_info = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }
    
    # 1. 提取视频信息
    try:
        with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as e:
        st.error(f"❌ 无法解析链接：{e}")
        st.stop()
    
    if info is None:
        st.error("❌ 未提取到任何视频信息，请检查链接或视频是否可用。")
        st.stop()
    
    # 获取标题
    title = info.get('title', 'video')
    # 保留安全文件名
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_', '-')).rstrip()
    
    # 列出所有可用格式
    formats = info.get('formats', [])
    if not formats:
        st.warning("⚠️ 没有可下载的格式。可能是 DRM 保护内容或需登录。")
        st.stop()
    
    # 构建格式选项
    format_options = {}
    for f in formats:
        # 过滤掉没有视频的格式
        if f.get('vcodec') == 'none':
            continue
        fmt_id = f['format_id']
        note = f.get('format_note', '')
        ext = f.get('ext', '')
        resolution = f.get('resolution', 'unknown')
        filesize = f.get('filesize')
        size_str = f"{filesize / 1024 / 1024:.1f}MB" if filesize else "未知大小"
        label = f"{fmt_id} - {resolution} ({note}) {ext} - {size_str}"
        format_options[label] = fmt_id
    
    if not format_options:
        st.warning("⚠️ 未找到可下载的视频流。")
        st.stop()
    
    st.success(f"✅ 解析成功：{title}")
    
    # 2. 选择格式
    selected_label = st.selectbox("选择下载画质", list(format_options.keys()))
    selected_fmt = format_options[selected_label]
    
    # 3. 下载按钮
    if st.button("⬇️ 下载视频"):
        # 输出路径
        out_file = os.path.join(tmp_dir, f"{safe_title}.%(ext)s")
        ydl_opts_download = {
            'format': selected_fmt,
            'outtmpl': out_file,
            'quiet': True,
            'no_warnings': True,
            'noprogress': True,
            'retries': 3,
        }
        
        with st.spinner("正在下载，请稍候..."):
            try:
                with yt_dlp.YoutubeDL(ydl_opts_download) as ydl:
                    ydl.download([url])
            except Exception as e:
                st.error(f"下载失败：{e}")
                st.stop()
        
        # 找到生成的文件
        downloaded_files = os.listdir(tmp_dir)
        video_file = None
        for fname in downloaded_files:
            if fname.startswith(safe_title) and not fname.endswith('.part'):
                video_file = os.path.join(tmp_dir, fname)
                break
        
        if video_file:
            # 提供下载按钮
            with open(video_file, 'rb') as f:
                video_bytes = f.read()
            st.download_button(
                label="📥 点击保存视频",
                data=video_bytes,
                file_name=os.path.basename(video_file),
                mime="video/mp4",
            )
        else:
            st.error("找不到下载完成的文件，请重试。")
    
    # 清理临时目录（仅当应用关闭时，这里可以在会话结束后手动清理，简化处理）
    # 实际部署建议定期清理临时文件
    st.caption("💡 下载完成后请及时保存，关闭页面后临时文件将被清除。")

else:
    st.info("👆 请在上方输入有效的亚马逊视频链接")
