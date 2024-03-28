import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.time.Instant;
import java.util.concurrent.TimeUnit;

public class CrptApi {
    private TimeUnit timeUnit;
    private int requestLimit;
    private int currentRequestCount;
    private Instant lastRequestTime;

    // Конструктор класса
    public CrptApi(TimeUnit timeUnit, int requestLimit) {
        this.timeUnit = timeUnit;
        this.requestLimit = requestLimit;
        this.currentRequestCount = 0;
        this.lastRequestTime = Instant.now();
    }

    // Создание документа
    public synchronized void CreateDocument(String json) throws IOException {

        String link = "https://ismp.crpt.ru/api/v3/lk/documents/create";
        HttpURLConnection httpURLConnection;
        Instant currentTime = Instant.now();

        // Проверяем, прошло ли достаточно времени для сброса счетчика запросов
        if (timeUnit.convert(currentTime.getEpochSecond() - lastRequestTime.getEpochSecond(), TimeUnit.SECONDS) > timeUnit.toSeconds(1)) {
            currentRequestCount = 0;
            lastRequestTime = currentTime;
        }

        // Проверяем, не превышен ли лимит запросов
        if (currentRequestCount < requestLimit) {

            // Выполняем запрос
            try {
                URL url = new URL(link);
                httpURLConnection = (HttpURLConnection) url.openConnection();
                httpURLConnection.setRequestMethod("POST");
                httpURLConnection.setRequestProperty("Content-Type", "application/json");
                httpURLConnection.setDoOutput(true);

                try (OutputStream os = httpURLConnection.getOutputStream()) {
                    byte[] input = json.getBytes("utf-8");
                    os.write(input, 0, input.length);
                }

                // Получение ответа
                try (BufferedReader br = new BufferedReader(new InputStreamReader(httpURLConnection.getInputStream(), "utf-8"))) {
                    StringBuilder response = new StringBuilder();
                    String responseLine = null;
                    while ((responseLine = br.readLine()) != null) {
                        response.append(responseLine.trim());
                    }
                    System.out.println(response.toString());
                }
                httpURLConnection.disconnect();
                currentRequestCount++;
                lastRequestTime = currentTime;
            } catch (IOException e) {
                throw new RuntimeException(e);
            }

        } else {

            // Заблокировать запрос
            System.out.println("Превышен лимит запросов. Блокировка запроса.");
        }
    }
}

public void main(String[] args) throws IOException {

    // Json документ
    String json = "{\"description\": {\"participantInn\": \"string\"}, \"doc_id\": \"string\", \"doc_status\": \"string\", \"doc_type\": \"LP_INTRODUCE_GOODS\", \"importRequest\": true, \"owner_inn\": \"string\", \"participant_inn\": \"string\", \"producer_inn\": \"string\", \"production_date\": \"2020-01-23\", \"production_type\": \"string\", \"products\": [{\"certificate_document\": \"string\", \"certificate_document_date\": \"2020-01-23\", \"certificate_document_number\": \"string\", \"owner_inn\": \"string\", \"producer_inn\": \"string\", \"production_date\": \"2020-01-23\", \"tnved_code\": \"string\", \"uit_code\": \"string\", \"uitu_code\": \"string\"}], \"reg_date\": \"2020-01-23\", \"reg_number\": \"string\"}";

    // Создание объекта класса
    CrptApi object = new CrptApi(TimeUnit.MINUTES, 3);

    // Создание документа
    object.CreateDocument(json);
}
