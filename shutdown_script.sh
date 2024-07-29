#!/bin/bash

# Загрузка переменных из .env файла
export $(grep -v '^#' /root/telegram_message_saver/.env | xargs)

# Имя лог-файла
LOG_FILE="server_shutdown.log"

# Список IP-адресов серверов
SERVERS=(
    "192.168.179.215"
    "192.168.179.219"
    "192.168.179.210"
    "192.168.179.185"
    "192.168.179.187"
    "192.168.179.189"
    "192.168.179.208"
    "192.168.179.226"
    "192.168.179.242"
    "192.168.179.249"
    "192.168.179.183"
    "192.168.179.188"
    "192.168.179.181"
    "192.168.179.211"
    "192.168.179.248"
    "192.168.179.186"
    "192.168.179.225"
    "192.168.179.214"
    "192.168.179.228"
    "192.168.179.182"
)

# Функция для логирования и вывода на экран
log() {
    local message="$(date '+%Y-%m-%d %H:%M:%S') - $1"
    echo "$message" | tee -a "$LOG_FILE"
}

# Функция для проверки доступности сервера и его выключения
check_and_shutdown_server() {
    local ip=$1
    log "Проверка доступности сервера $ip..."

    if sshpass -p "$SSH_PASS" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=$SSH_TIMEOUT -p "$SSH_PORT" "$SSH_USER@$ip" "exit" 2>/dev/null; then
        log "Сервер $ip доступен. Отправка команды выключения..."
        sshpass -p "$SSH_PASS" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=$SSH_TIMEOUT -p "$SSH_PORT" "$SSH_USER@$ip" "sudo shutdown -h now" 2>/dev/null
        log "Команда выключения отправлена на сервер $ip"
        return 0
    else
        log "Сервер $ip недоступен"
        return 1
    fi
}

# Массивы для хранения результатов
successful_shutdowns=()
failed_shutdowns=()

# Основной процесс
log "Начало процесса выключения серверов"
for ip in "${SERVERS[@]}"; do
    if check_and_shutdown_server "$ip"; then
        successful_shutdowns+=("$ip")
    else
        failed_shutdowns+=("$ip")
    fi
    log "Текущий статус:"
    log "Успешно выключены: ${successful_shutdowns[*]:-Нет}"
    log "Не удалось выключить: ${failed_shutdowns[*]:-Нет}"
    log "---"
done

# Функция для форматирования вывода
format_output() {
    local title="$1"
    shift
    local items=("$@")

    if [ ${#items[@]} -eq 0 ]; then
        echo "$title Нет"
    else
        echo "$title ${items[*]}"
    fi
}

# Вывод итоговых результатов
log "Итоговые результаты выключения серверов:"
log "$(format_output "Успешно выключены:" "${successful_shutdowns[@]}")"
log "$(format_output "Не удалось выключить:" "${failed_shutdowns[@]}")"

# Форматированный вывод для Telegram
telegram_output="Процесс выключения завершен"
telegram_output+="%0A$(format_output "Успешно выключены:" "${successful_shutdowns[@]}")"
telegram_output+="%0A$(format_output "Не удалось выключить:" "${failed_shutdowns[@]}")"

# Отправка сообщения в Telegram
curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
     -d chat_id="$CHAT_ID" \
     -d text="$telegram_output" \
     -d parse_mode="HTML"

log "Процесс завершен. Проверьте файл $LOG_FILE для подробной информации."
