<template>
    <uploader
        :options="options"
        class="uploader-example"
        @file-complete="fileComplete"
    >
        <uploader-unsupport />
        <uploader-drop>
            <p>Drop files here to upload or</p>
            <uploader-btn
                :attrs="attrs"
                :single="true"
            >
                select images
            </uploader-btn>
        </uploader-drop>
        <uploader-list />
    </uploader>
</template>

<script>
export default {
    data() {
        return {
            options: {
                target:     '//localhost:8080/board-service/file/upload',
                singleFile: true,
                testChunks: true,
            },
            attrs: {

            },
        };
    },
    methods: {
        async fileComplete() {
            console.log('file complete', arguments);
            const file = arguments[0].file;

            const url =
                '//localhost:8080/data-fusion-service/file/merge?filename=' +
                file.name +
                '&uniqueIdentifier=' +
                arguments[0].uniqueIdentifier;

            const { code } = await this.$http.get({
                url,
            });

            this.$axios
                .get(url)
                .then(function(response) {
                    console.log(response);
                })
                .catch(function(error) {
                    console.log(error);
                });
        },
    },
};
</script>

<style>
.uploader-example {
    width: 880px;
    padding: 15px;
    margin: 40px auto 0;
    font-size: 12px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.4);
}
.uploader-example .uploader-btn {
    margin-right: 4px;
}
.uploader-example .uploader-list {
    max-height: 440px;
    overflow: auto;
    overflow-x: hidden;
    overflow-y: auto;
}
</style>
