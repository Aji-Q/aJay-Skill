// macOS local-only portrait segmentation. No uploads or image regeneration.
// Build: clang -fobjc-arc -fno-modules -framework Foundation -framework Vision \
//   -framework CoreImage -framework CoreGraphics -framework CoreVideo create_speaker_masks.m -o /tmp/jtrader-mask
// Run: /tmp/jtrader-mask INPUT_IMAGE OUTPUT_MASK.png
// Accurate person segmentation was visually selected over generic foreground
// instance segmentation: it preserves finer white hair without a black halo.
#import <Foundation/Foundation.h>
#import <Vision/Vision.h>
#import <CoreImage/CoreImage.h>
int main(int argc, const char *argv[]) {
    @autoreleasepool {
        if (argc != 3) { fprintf(stderr, "Usage: jtrader-mask INPUT_IMAGE OUTPUT_MASK.png\n"); return 2; }
        if (@available(macOS 12.0, *)) {
            NSDate *start = NSDate.date;
            NSError *error = nil;
            NSURL *input = [NSURL fileURLWithPath:@(argv[1])];
            NSURL *output = [NSURL fileURLWithPath:@(argv[2])];
            VNImageRequestHandler *handler = [[VNImageRequestHandler alloc] initWithURL:input options:@{}];
            VNGeneratePersonSegmentationRequest *request = [VNGeneratePersonSegmentationRequest new];
            request.revision = VNGeneratePersonSegmentationRequestRevision1;
            request.qualityLevel = VNGeneratePersonSegmentationRequestQualityLevelAccurate;
            request.outputPixelFormat = kCVPixelFormatType_OneComponent8;
            if (![handler performRequests:@[request] error:&error]) {
                fprintf(stderr, "%s\n", error.description.UTF8String); return 1;
            }
            VNPixelBufferObservation *observation = request.results.firstObject;
            if (!observation) { fprintf(stderr, "No person mask returned.\n"); return 1; }
            CIImage *source = [CIImage imageWithContentsOfURL:input];
            CIImage *image = [CIImage imageWithCVPixelBuffer:observation.pixelBuffer];
            CGSize maskSize = image.extent.size;
            image = [image imageByApplyingTransform:CGAffineTransformMakeScale(
                source.extent.size.width / maskSize.width,
                source.extent.size.height / maskSize.height)];
            CIContext *context = [CIContext contextWithOptions:@{kCIContextCacheIntermediates:@NO}];
            CGColorSpaceRef gray = CGColorSpaceCreateDeviceGray();
            BOOL ok = [context writePNGRepresentationOfImage:image toURL:output format:kCIFormatL8 colorSpace:gray options:@{} error:&error];
            CGColorSpaceRelease(gray);
            if (!ok) { fprintf(stderr, "%s\n", error.description.UTF8String); return 1; }
            printf("%s: accurate person mask %.0fx%.0f -> %.0fx%.0f, %.3f sec\n",input.lastPathComponent.UTF8String,maskSize.width,maskSize.height,image.extent.size.width,image.extent.size.height,-start.timeIntervalSinceNow);
            return 0;
        }
        fprintf(stderr, "Requires macOS 12 or newer.\n"); return 2;
    }
}
