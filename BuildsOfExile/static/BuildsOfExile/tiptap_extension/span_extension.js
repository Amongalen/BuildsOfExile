import {Mark} from 'https://cdn.skypack.dev/pin/@tiptap/core@v2.0.0-beta.29-ehyNSRjShPZE49ePTtXD/mode=imports,min/optimized/@tiptap/core.js'

export class SpanExtension extends Mark {
    get name() {
        return 'SpanExtension'
    }

    get schema() {
        return {
            attrs: {
                class: {
                    default: 'some-class',
                },
            },
            inclusive: false,
            parseDOM: [
                {
                    tag: 'span[class]',
                    getAttrs: dom => ({
                        class: dom.getAttribute('class'),
                    }),
                },
            ],
            toDOM: node => ['span', {
                ...node.attrs,
            }, 0],
        }
    }
}