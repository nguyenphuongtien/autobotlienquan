## Bước 1: Tạo bot trên telegram
- Tìm bot father trên telegram (@BotFather đây là username của botfather)
- /newbot >> nhập tên bot >> nhập username cho bot
- Lưu lại token của bot

## Bước 2: Config bot
- Theo dỗi trong file configbot.py, ngôn ngữ áp dụng python

## Build 3: Build image docker
- Cấu hình docker file chi tiết theo dỗi trong file Dockerfile
- Chạy lệnh `docker build -t lienquanbot:0.0.1 .`
- Trong đó `lienquanbot:0.0.1` là tên image, `0.0.1` là version của image `. build với Dockerfile trong thư mục hiện tại`
- Chạy lệnh `docker run -d --name lienquanbot lienquanbot:0.0.1` để start container.